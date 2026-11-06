import ast
import json
from pathlib import Path
from random import choice

import yaml
from qgis.core import QgsApplication, QgsSettings
from qgis.PyQt.QtCore import QUrl, QUrlQuery
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtNetwork import QNetworkRequest

from .qgis_utils import log_message

TIANDITU_HOME_URL = "https://www.tianditu.gov.cn/"
PLUGIN_NAME = "tianditu-tools"

PluginDir = Path(__file__).parent

HEADER = {
    "User-Agent": "Mozilla/5.0 QGIS/32400/Windows 10 Version 2009",
    "Referer": "https://www.tianditu.gov.cn/",
}

# QGIS 仅在用户自定义过界面字体时才写入 app/fontFamily，
# 读取不到时回退到当前应用字体，避免构造出无字族的 QFont
APP_FONT = QgsSettings().value("app/fontFamily") or QFont().family()

SUBDOMAINS = tuple(f"t{i}" for i in range(8))


def get_point_style():
    # current_qgis_version = Qgis.QGIS_VERSION_INT
    # if current_qgis_version <= 31616:
    #     return str(PluginDir.joinpath("./Styles/PointStyle_316.qml"))
    return str(PluginDir.joinpath("./Styles/PointStyle.qml"))


def get_extramap_status():
    default_status = {}
    sections = ["tianditu_province", "extra"]
    for section in sections:
        json_path = PluginDir.joinpath(f"maps/{section}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        default_status[section] = list(data.keys())
    return default_status


class PluginConfig:
    def __init__(self):
        self.conf = QgsSettings()
        self.conf_name = "tianditu-tools"
        self.section_tianditu = f"{self.conf_name}/Tianditu"

    def init_config(self):
        # 初始化配置文件
        if not self.conf.contains("tianditu-tools/Tianditu/key"):
            log_message("初始化配置文件")
            # 初始化
            self.conf.setValue(f"{self.section_tianditu}/key", "")
            self.conf.setValue(f"{self.section_tianditu}/keyList", "")
            self.conf.setValue(f"{self.section_tianditu}/random", True)
            self.conf.setValue(f"{self.section_tianditu}/random_key", False)
            self.conf.setValue(f"{self.section_tianditu}/subdomain", "t0")
        if not self.conf.contains("tianditu-tools/Other/extramap_status"):
            log_message("初始化 extra map 文件")
            self.set_extra_maps_status(get_extramap_status())
        # 升级到保存多个key的版本
        if not self.conf.contains(f"{self.section_tianditu}/keyList"):
            self.conf.setValue(f"{self.section_tianditu}/random_key", False)
            # 保存原来的key
            if self.get_key() != "":
                self.conf.setValue(f"{self.section_tianditu}/keyList", self.get_key())
            else:
                self.conf.setValue(f"{self.section_tianditu}/keyList", "")

    @property
    def key_list(self):
        """已保存的天地图 key 列表"""
        data_str = self.get_value("Tianditu/keyList") or ""
        return [key.strip() for key in data_str.split(",") if key.strip()]

    @key_list.setter
    def key_list(self, keys):
        self.conf.setValue(f"{self.section_tianditu}/keyList", ",".join(keys))

    @property
    def active_key(self):
        """当前使用的 key，未设置时返回空字符串"""
        return self.get_key() or ""

    @active_key.setter
    def active_key(self, key):
        self.set_key(key or "")

    @property
    def random_key(self):
        return self.get_bool_value("Tianditu/random_key")

    @random_key.setter
    def random_key(self, enabled):
        self.set_value("Tianditu/random_key", bool(enabled))

    @property
    def random_subdomain(self):
        return self.get_bool_value("Tianditu/random")

    @random_subdomain.setter
    def random_subdomain(self, enabled):
        self.set_value("Tianditu/random", bool(enabled))

    @property
    def subdomain(self):
        value = self.get_value("Tianditu/subdomain")
        return value if value in SUBDOMAINS else SUBDOMAINS[0]

    @subdomain.setter
    def subdomain(self, value):
        if value in SUBDOMAINS:
            self.set_value("Tianditu/subdomain", value)

    def get_key_list(self):
        return self.key_list

    def save_key_list(self, data_list):
        self.key_list = data_list

    def get_extra_maps_status(self):
        """返回各分组启用的地图名列表，缺失的分组用默认值补齐"""
        data_str = self.get_value("Other/extramap_status") or ""
        data = {}
        if data_str:
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                # 兼容旧版本用 str(dict) 保存的格式
                try:
                    data = ast.literal_eval(data_str)
                except (ValueError, SyntaxError):
                    data = {}
        if not isinstance(data, dict):
            data = {}
        defaults = get_extramap_status()
        return {
            section: data.get(section, default) for section, default in defaults.items()
        }

    def set_extra_maps_status(self, data):
        self.set_value("Other/extramap_status", json.dumps(data, ensure_ascii=False))

    def get_value(self, name):
        return self.conf.value(f"{self.conf_name}/{name}")

    def get_bool_value(self, name):
        return self.conf.value(f"{self.conf_name}/{name}", type=bool)

    def set_value(self, name, value):
        self.conf.setValue(f"{self.conf_name}/{name}", value)

    def get_key(self):
        return self.get_value("Tianditu/key") or ""

    def get_random_key(self):
        key_list = self.key_list
        return choice(key_list) if key_list else ""

    def set_key(self, key):
        key_to_set = ""
        if key is not None:
            key_to_set = key
        self.conf.setValue(f"{self.section_tianditu}/key", key_to_set)


def make_request(url: str, referer: str = None, params=None):
    u = QUrl(url)
    query = QUrlQuery()
    if params:
        for key, value in params.items():
            query.addQueryItem(key, value)
        u.setQuery(query)
    request = QNetworkRequest(u)
    # request.setHeader(QNetworkRequest.UserAgentHeader, headers["User-Agent"]) # 设置 User-Agent 无效
    if referer:
        request.setRawHeader(b"Referer", referer.encode("utf-8"))

    return request


def tianditu_map_url(maptype: str, token: str, subdomain: str) -> str:
    """
    返回天地图url

    Args:
        maptype (str): 类型
        token (str): 天地图key
        subdomain (str): 使用的子域名

    Returns:
        str: 返回天地图XYZ瓦片地址
    """
    domain = f"https://{subdomain}.tianditu.gov.cn"
    # if maptype == "terrain-rgb":
    #     domain = "https://lcdata.tianditu.gov.cn"
    url = f"{domain}/{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}"
    url += "&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}"
    url += f"&tk={token}"
    return url


# 天地图 EPSG:4490 瓦片的本地 capabilities 模板，其中的 {tk} 在生成时替换为实际 key
WMTS_C_TEMPLATE = PluginDir.joinpath("maps/tianditu_c.xml")


def tianditu_wmts_c_capabilities(key: str, subdomain: str = "t6") -> Path:
    """生成（或复用）天地图 EPSG:4490 瓦片的本地 WMTS capabilities 文件

    官方 capabilities 有两个坑：GetTile 端点不带 tk 会导致瓦片 403；
    ScaleDenominator 按 96 DPI 计算会导致比例尺偏移 5.83%。
    内置模板已修补这两点（ResourceURL 模板带 tk、比例尺按 0.28mm 重算），
    这里只用实际的 key 和子域名替换模板，QGIS 便能按 REST 方式取瓦片。

    Args:
        key (str): 天地图 key
        subdomain (str): 使用的子域名，默认 t6

    Returns:
        Path: 本地 capabilities 文件路径
    """
    caps_dir = Path(QgsApplication.qgisSettingsDirPath()).joinpath(
        "tianditu_tools", "caps_c"
    )
    caps_file = caps_dir.joinpath("WMTSCapabilities.xml")
    domain = f"https://{subdomain}.tianditu.gov.cn"

    content = WMTS_C_TEMPLATE.read_text(encoding="utf-8")
    content = content.replace("tk={tk}", f"tk={key}")
    content = content.replace("https://t6.tianditu.gov.cn", domain)
    # 内容完全一致才复用，模板改动、换 key、换子域名都会重新生成
    if caps_file.exists():
        try:
            if caps_file.read_text(encoding="utf-8") == content:
                return caps_file
        except OSError:
            pass

    caps_dir.mkdir(parents=True, exist_ok=True)
    caps_file.write_text(content, encoding="utf-8")
    return caps_file


def load_yaml(file_path: Path):
    """
    读取YAML文件
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
