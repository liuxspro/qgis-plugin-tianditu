from random import choice

from qgis.PyQt.QtWidgets import QMenu, QToolButton

from ...compat import MenuButtonPopup
from ...qgis_utils import add_raster_layer, add_raster_layer_group, push_error
from ...utils import (
    SUBDOMAINS,
    TIANDITU_HOME_URL,
    PluginConfig,
    PluginDir,
    tianditu_map_url,
    tianditu_wmts_c_capabilities,
)
from ..icons import icons
from .extra_map import add_extra_map_menu, add_tianditu_province_menu
from .utils import get_local_wmts_uri, get_xyz_uri

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

# EPSG:4490（经纬度）图层，使用内置的本地 WMTS capabilities
# terrain-rgb 没有 _c 版本，故不在其中
# name: 图层名称, layer: capabilities 中的图层标识, format: 图层声明的 Format
tianditu_c_map_info = {
    "vec": {
        "name": "天地图-矢量地图",
        "layer": "tianditu_vec_c",
        "format": "image/png",
    },
    "cva": {
        "name": "天地图-矢量注记",
        "layer": "tianditu_cva_c",
        "format": "image/png",
    },
    "img": {
        "name": "天地图-影像地图",
        "layer": "tianditu_img_c",
        "format": "image/jpeg",
    },
    "cia": {
        "name": "天地图-影像注记",
        "layer": "tianditu_cia_c",
        "format": "image/png",
    },
    "ter": {
        "name": "天地图-地形晕染",
        "layer": "tianditu_ter_c",
        "format": "image/jpeg",
    },
    "cta": {
        "name": "天地图-地形注记",
        "layer": "tianditu_cta_c",
        "format": "image/png",
    },
    "ibo": {
        "name": "天地图-全球境界",
        "layer": "tianditu_ibo_c",
        "format": "image/png",
    },
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
        self.setMenu(menu)
        self.refresh_menu()
        self.setPopupMode(MenuButtonPopup)
        self.setIcon(self.icons["add"])

    def refresh_menu(self):
        """重建菜单内容（地图源开关变化时调用）"""
        menu = self.menu()
        menu.clear()

        # 单个图层
        for map_type, map_name in tianditu_map_info.items():
            menu.addAction(
                self.icons["map"],
                map_name,
                lambda maptype_=map_type: self.add_tianditu_basemap(maptype_),
            )
        menu.addSeparator()

        # EPSG:4490 图层（本地 wmts）
        self._add_tianditu_c_menu(menu)
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

    def _add_tianditu_c_menu(self, parent_menu):
        """添加 EPSG:4490 图层子菜单（本地 WMTS capabilities）"""
        menu = parent_menu.addMenu(self.icons["epsg4490"], "EPSG:4490 图层")
        for map_type, map_info in tianditu_c_map_info.items():
            menu.addAction(
                self.icons["epsg4490"],
                f"{map_info['name']}(EPSG:4490)",
                lambda maptype_=map_type: self.add_tianditu_c_basemap(maptype_),
            )
        menu.addSeparator()
        for group_key, group_info in tianditu_map_groups.items():
            menu.addAction(
                self.icons["epsg4490"],
                f"{group_info['name']}(4490)",
                lambda key=group_key: self.add_tianditu_c_basemap_group(key),
            )

    def _get_tianditu_c_capabilities(self):
        """生成本地 WMTS capabilities，失败时返回 None"""
        cred = self._get_tianditu_credentials()
        if cred is None:
            return None
        key, subdomain = cred
        try:
            return tianditu_wmts_c_capabilities(key, subdomain)
        except OSError as err:
            push_error(self.iface, "错误", f"生成 EPSG:4490 图层配置失败: {err}")
            return None

    def _get_tianditu_credentials(self):
        """获取天地图 key 和 subdomain，key 无效时返回 None"""
        key = conf.active_key
        if not key:
            keys = conf.key_list
            key = keys[0] if keys else ""
        if not key:
            push_error(self.iface, "错误", "天地图 Key 未设置或 Key 无效")
            return None

        if conf.random_subdomain:
            subdomain = choice(SUBDOMAINS)
        else:
            subdomain = conf.subdomain
        if conf.random_key:
            key = conf.get_random_key() or key
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

    def add_tianditu_c_basemap(self, maptype):
        """添加天地图 EPSG:4490 单图层"""
        caps_file = self._get_tianditu_c_capabilities()
        if caps_file is None:
            return
        map_info = tianditu_c_map_info[maptype]
        uri = get_local_wmts_uri(caps_file, map_info["layer"], map_info["format"])
        add_raster_layer(uri, f"{map_info['name']}(4490)")

    def add_tianditu_c_basemap_group(self, group_key):
        """添加天地图 EPSG:4490 图层组（含注记）"""
        caps_file = self._get_tianditu_c_capabilities()
        if caps_file is None:
            return

        group_info = tianditu_map_groups[group_key]
        layers = []
        for maptype in group_info["layers"]:
            map_info = tianditu_c_map_info[maptype]
            uri = get_local_wmts_uri(caps_file, map_info["layer"], map_info["format"])
            layers.append((uri, f"{map_info['name']}(4490)"))

        add_raster_layer_group(layers, f"{group_info['name']}(4490)")
