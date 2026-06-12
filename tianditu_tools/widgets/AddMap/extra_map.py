import json

from qgis.PyQt.QtWidgets import QMenu

from ...qgis_utils import add_raster_layer
from ...utils import PluginConfig, PluginDir
from ..icons import get_extra_map_icon, icons
from .sd import SdAction
from .utils import get_xyz_uri

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
    extra_maps_status = conf.get_extra_maps_status()
    # load tianditu_province.json
    tianditu_province_json_path = PluginDir.joinpath("maps/tianditu_province.json")
    with open(tianditu_province_json_path, "r", encoding="utf-8") as f:
        tianditu_province_json = json.load(f)
    for map_name, map_data in tianditu_province_json.items():
        if map_name in extra_maps_status["tianditu_province"]:
            add_map_action = parent_menu.addAction(icons["map"], map_name)
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
    extra_json_path = PluginDir.joinpath("maps/extra.json")
    with open(extra_json_path, "r", encoding="utf-8") as f:
        extra = json.load(f)
    extra_root = parent_menu.addAction(icons["other"], "其他地图")
    extra_root_menu = QMenu(parent_menu)
    maps = extra.keys()
    extra_maps_status = conf.get_extra_maps_status()
    for map_name in maps:
        if map_name in extra_maps_status["extra"]:
            map_data = extra[map_name]
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
