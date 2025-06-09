from qgis.PyQt.QtWidgets import QMenu

from .sd import SdAction
from .utils import add_raster_layer, get_xyz_uri
from ..icons import icons, get_extra_map_icon
from ...utils import PluginDir, load_yaml, PluginConfig

conf = PluginConfig()


def add_map(data):
    name = data["name"]
    map_type = data.get("type")
    add_map_type = "wms"
    uri = data.get("uri", "")
    referer = data.get("referer", "")
    if uri == "":
        uri = get_xyz_uri(data["url"], data["zmin"], data["zmax"], referer)

    if map_type == "arcgismapserver":
        add_map_type = "arcgismapserver"

    add_raster_layer(uri, name, add_map_type)


def add_tianditu_province_menu(parent_menu: QMenu, iface):
    # 增加山东天地图
    sd = SdAction(iface, parent=parent_menu)
    parent_menu.addAction(sd)
    parent_menu.addSeparator()
    # 其他省份
    tianditu_province_path = PluginDir.joinpath("maps/tianditu_province.yml")
    tianditu_province = load_yaml(tianditu_province_path)["maps"]
    maps = tianditu_province.keys()
    extra_maps_status = conf.get_extra_maps_status()
    for map_name in maps:
        # 一级菜单 省份名称
        if map_name in extra_maps_status["tianditu_province"]:
            add_map_action = parent_menu.addAction(icons["map"], map_name)
            map_data = tianditu_province[map_name]
            sub_menu = QMenu(parent_menu)
            for m in map_data:
                sub_menu.addAction(
                    icons["map"],
                    m["name"],
                    lambda m_=m: add_map(m_),
                )
            add_map_action.setMenu(sub_menu)
    parent_menu.addSeparator()


def add_extra_map_menu(parent_menu: QMenu):
    extra = load_yaml(PluginDir.joinpath("maps/extra.yml"))
    extra_maps = extra["maps"]
    extra_root = parent_menu.addAction(icons["other"], "其他地图")
    extra_root_menu = QMenu(parent_menu)
    maps = extra_maps.keys()
    extra_maps_status = conf.get_extra_maps_status()
    for map_name in maps:
        if (
            map_name in extra_maps_status["tianditu_province"]
            or map_name in extra_maps_status["extra"]
        ):
            map_data = extra_maps[map_name]
            sub_menu = extra_root_menu.addAction(icons["other"], map_name)
            sub_sub_menu = QMenu(parent_menu)
            for sub_map in map_data:
                sub_sub_menu.addAction(
                    get_extra_map_icon(sub_map.get("icon", "default.svg")),
                    sub_map["name"],
                    lambda m_=sub_map: add_map(m_),
                )
            sub_menu.setMenu(sub_sub_menu)
    extra_root.setMenu(extra_root_menu)
