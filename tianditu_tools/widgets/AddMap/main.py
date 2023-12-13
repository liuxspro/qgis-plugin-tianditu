import random

import requests
import yaml
from qgis.PyQt.QtWidgets import QToolButton, QMenu, QMessageBox
from qgis.core import Qgis, QgsProject, QgsRasterLayer

from tianditu_tools.utils import (
    TIANDITU_HOME_URL,
    PluginConfig,
    tianditu_map_url,
    PluginDir,
)
from tianditu_tools.widgets.icons import icons


def add_raster_layer(uri: str, name: str, provider_type: str = "wms") -> None:
    """QGIS 添加 xyz(wms) 图层

    Args:
        uri (str): 栅格图层uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)
    Reference: https://qgis.org/pyqgis/3.32/core/QgsRasterLayer.html
    """
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    QgsProject.instance().addMapLayer(raster_layer)


tianditu_map_info = {
    "vec": "天地图-矢量地图",
    "cva": "天地图-矢量注记",
    "img": "天地图-影像地图",
    "cia": "天地图-影像注记",
    "ter": "天地图-地形晕染",
    "cta": "天地图-地形注记",
    "eva": "天地图-英文矢量注记",
    "eia": "天地图-英文影像注记",
    "ibo": "天地图-全球境界",
}

conf = PluginConfig()

tianditu_province_path = PluginDir.joinpath("maps/tianditu_province.yml")
with open(tianditu_province_path, "r", encoding="utf-8") as f:
    tianditu_province = list(yaml.safe_load_all(f))[1]


def get_map_uri(url: str, zmin: int = 0, zmax: int = 18, referer: str = "") -> str:
    """返回瓦片地图uri

    Args:
        url (str): 瓦片地图url
        zmin (int, optional): z 最小值. Defaults to 0.
        zmax (int, optional): z 最大值 Defaults to 18.
        referer (str, optional): Referer. Defaults to "".

    Returns:
        str: 瓦片地图uri
    """
    # "?" 进行 URL 编码后, 在 3.34 版本上无法加载地图
    # "&"是必须要进行 url 编码的
    current_qgis_version = Qgis.QGIS_VERSION_INT
    url_quote = requests.utils.quote(url, safe=":/?=")
    uri = f"type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}"
    if referer != "":
        if current_qgis_version >= 32600:
            uri += f"&http-header:referer={referer}"
        else:
            uri += f"&referer={referer}"
    return uri


class AddMapBtn(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.setToolTip("添加地图")
        self.setup_action()

    def setup_action(self):
        menu = QMenu(self)
        menu.setObjectName("TianDiTuAddMap")
        for map_type, map_name in tianditu_map_info.items():
            menu.addAction(
                self.icons["map"],
                map_name,
                lambda maptype_=map_type: self.add_tianditu_basemap(maptype_),
            )
        menu.addSeparator()
        # 天地图省级节点
        keys = tianditu_province.keys()
        for key in keys:
            province_action = menu.addAction(icons["map"], key)
            province_menu = QMenu()
            map_data = tianditu_province[key]
            for m in map_data:
                province_menu.addAction(
                    icons["map"],
                    m["name"],
                    lambda m_=m: add_raster_layer(
                        m_["uri"], m_["name"], m_.get("type", "wms")
                    ),
                )
            province_action.setMenu(province_menu)
        menu.addSeparator()
        # 其他图源
        # extra = menu.addAction(icons["other"], "其他图源")
        # extra_map_menu = QMenu()
        self.setMenu(menu)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.setIcon(self.icons["add"])

    def add_tianditu_basemap(self, maptype):
        key = conf.get_key()
        keyisvalid = conf.get_bool_value("Tianditu/keyisvalid")
        if key == "" or keyisvalid is False:
            QMessageBox.warning(
                self, "错误", "天地图Key未设置或Key无效", QMessageBox.Yes, QMessageBox.Yes
            )
        else:
            random_enabled = conf.get_bool_value("Tianditu/random")
            if random_enabled:
                subdomain = random.choice(
                    ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7"]
                )
                map_url = tianditu_map_url(maptype, key, subdomain)
                uri = get_map_uri(map_url, 1, 18, TIANDITU_HOME_URL)
                add_raster_layer(uri, tianditu_map_info[maptype])
