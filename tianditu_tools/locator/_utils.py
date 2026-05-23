from ..utils import PluginConfig

_LEVEL_NAMES = {5: "国家级", 4: "省级", 3: "市级", 2: "区县级"}


def get_api_key(conf):
    """从 PluginConfig 获取天地图 API key"""
    if conf.get_bool_value("Tianditu/random_key"):
        return conf.get_random_key()
    key = conf.get_key()
    if not key:
        key = conf.get_value("Tianditu/keyList")
        if key:
            keys = key.split(",")
            if keys:
                key = keys[0].strip()
    return key or ""


__all__ = ["_LEVEL_NAMES", "get_api_key"]
