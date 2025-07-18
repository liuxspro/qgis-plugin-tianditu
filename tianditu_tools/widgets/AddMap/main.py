import random

from qgis.PyQt.QtWidgets import QToolButton, QMenu, QMessageBox

from .extra_map import add_tianditu_province_menu, add_extra_map_menu
from .utils import get_xyz_uri
from ..icons import icons
from ...compat import MenuButtonPopup
from ...qgis_utils import add_raster_layer
from ...utils import TIANDITU_HOME_URL, PluginConfig, tianditu_map_url, PluginDir

tianditu_map_info = {
    "vec": "天地图-矢量地图",
    "cva": "天地图-矢量注记",
    "img": "天地图-影像地图",
    "cia": "天地图-影像注记",
    "ter": "天地图-地形晕染",
    "cta": "天地图-地形注记",
    "ibo": "天地图-全球境界",
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
        for map_type, map_name in tianditu_map_info.items():
            menu.addAction(
                self.icons["map"],
                map_name,
                lambda maptype_=map_type: self.add_tianditu_basemap(maptype_),
            )
        # 山体阴影
        menu.addAction(self.icons["map"], "天地图-山体阴影", self.add_terrain_rgb)
        menu.addSeparator()
        # 天地图省级节点
        add_tianditu_province_menu(menu, self.iface)
        # 其他图源
        add_extra_map_menu(menu)
        self.setMenu(menu)
        self.setPopupMode(MenuButtonPopup)
        self.setIcon(self.icons["add"])

    def add_terrain_rgb(self):
        key = conf.get_key()
        if key == "":
            QMessageBox.warning(
                self,
                "错误",
                "天地图Key未设置或Key无效",
                QMessageBox.Yes,
                QMessageBox.Yes,
            )
            return
        map_url = tianditu_map_url("terrain-rgb", key, "")
        uri = get_xyz_uri(map_url, 1, 12, TIANDITU_HOME_URL)
        terrain_uri = "interpretation=maptilerterrain&" + uri
        terrain_layer = add_raster_layer(terrain_uri, "天地图-山体阴影")
        terrain_layer.loadNamedStyle(str(PluginDir.joinpath("./Styles/terrain.qml")))

    def add_tianditu_basemap(self, maptype):
        key = conf.get_key()
        if key == "":
            QMessageBox.warning(
                self,
                "错误",
                "天地图Key未设置或Key无效",
                QMessageBox.Yes,
                QMessageBox.Yes,
            )
        else:
            random_enabled = conf.get_bool_value("Tianditu/random")
            key_random_enabled = conf.get_bool_value("Tianditu/random_key")
            if random_enabled:
                subdomain = f"t{random.randint(0, 7)}"
            else:
                subdomain = conf.get_value("Tianditu/subdomain")
            if key_random_enabled:
                key = conf.get_random_key()
            map_url = tianditu_map_url(maptype, key, subdomain)
            uri = get_xyz_uri(map_url, 1, 18, TIANDITU_HOME_URL)
            add_raster_layer(uri, tianditu_map_info[maptype])
