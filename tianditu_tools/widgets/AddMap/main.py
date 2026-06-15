import random

from qgis.PyQt.QtWidgets import QMenu, QToolButton

from ...compat import MenuButtonPopup
from ...qgis_utils import add_raster_layer, add_raster_layer_group, push_error
from ...utils import TIANDITU_HOME_URL, PluginConfig, PluginDir, tianditu_map_url
from ..icons import icons
from .extra_map import add_extra_map_menu, add_tianditu_province_menu
from .utils import get_xyz_uri

tianditu_map_info = {
    "vec": "天地图-矢量地图",
    "cva": "天地图-矢量注记",
    "img": "天地图-影像地图",
    "cia": "天地图-影像注记",
    "ter": "天地图-地形晕染",
    "cta": "天地图-地形注记",
    "ibo": "天地图-全球境界",
    "terrain-rgb": "天地图-山体阴影",
}

tianditu_map_groups = {
    "vec+cva": {"name": "天地图-矢量地图(含注记)", "layers": ["cva", "vec"]},
    "img+cia": {"name": "天地图-影像地图(含注记)", "layers": ["cia", "img"]},
    "ter+cta": {"name": "天地图-地形晕染(含注记)", "layers": ["cta", "ter"]},
}

conf = PluginConfig()


class AddMapBtn(QToolButton):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.icons = icons
        self.setToolTip("添加地图")
        self.setup_action()

    def setup_action(self):
        menu = QMenu(self)
        menu.setObjectName("TianDiTuAddMap")

        # 单个图层
        for map_type, map_name in tianditu_map_info.items():
            menu.addAction(
                self.icons["map"],
                map_name,
                lambda maptype_=map_type: self.add_tianditu_basemap(maptype_),
            )
        menu.addSeparator()

        # 图层组（含注记）
        for group_key, group_info in tianditu_map_groups.items():
            menu.addAction(
                self.icons["map"],
                group_info["name"],
                lambda key=group_key: self.add_tianditu_basemap_group(key),
            )
        menu.addSeparator()

        # 天地图省级节点
        add_tianditu_province_menu(menu, self.iface)
        # 其他图源
        add_extra_map_menu(menu)
        self.setMenu(menu)
        self.setPopupMode(MenuButtonPopup)
        self.setIcon(self.icons["add"])

    def _get_tianditu_credentials(self):
        """获取天地图 key 和 subdomain，key 无效时返回 None"""
        key = conf.get_key()
        if key == "":
            push_error(self.iface, "错误", "天地图 Key 未设置或 Key 无效")
            return None

        random_enabled = conf.get_bool_value("Tianditu/random")
        key_random_enabled = conf.get_bool_value("Tianditu/random_key")
        if random_enabled:
            subdomain = f"t{random.randint(0, 7)}"
        else:
            subdomain = conf.get_value("Tianditu/subdomain")
        if key_random_enabled:
            key = conf.get_random_key()
        return key, subdomain

    def add_tianditu_basemap(self, maptype):
        cred = self._get_tianditu_credentials()
        if cred is None:
            return
        key, subdomain = cred
        map_url = tianditu_map_url(maptype, key, subdomain)

        if maptype == "terrain-rgb":
            uri = get_xyz_uri(map_url, 1, 12, TIANDITU_HOME_URL)
            terrain_uri = "interpretation=maptilerterrain&" + uri
            terrain_layer = add_raster_layer(terrain_uri, "天地图-山体阴影")
            terrain_layer.loadNamedStyle(
                str(PluginDir.joinpath("./Styles/terrain.qml"))
            )
            return

        uri = get_xyz_uri(map_url, 1, 18, TIANDITU_HOME_URL)
        add_raster_layer(uri, tianditu_map_info[maptype])

    def add_tianditu_basemap_group(self, group_key):
        """添加天地图图层组（含注记）"""
        cred = self._get_tianditu_credentials()
        if cred is None:
            return
        key, subdomain = cred

        group_info = tianditu_map_groups[group_key]
        layers = []
        for maptype in group_info["layers"]:
            map_url = tianditu_map_url(maptype, key, subdomain)
            uri = get_xyz_uri(map_url, 1, 18, TIANDITU_HOME_URL)
            layers.append((uri, tianditu_map_info[maptype]))

        add_raster_layer_group(layers, group_info["name"])
