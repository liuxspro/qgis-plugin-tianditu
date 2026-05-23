import json

import requests

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


def tianditu_request(url, params):
    """向天地图 API 发送 GET 请求并返回解析后的 JSON dict。
    请求失败、状态码非 200 或 JSON 解析失败时返回 None。
    """
    try:
        resp = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": "Mozilla/5.0 QGIS/32400/Windows 10 Version 2009",
                "Referer": "https://www.tianditu.gov.cn/",
            },
            timeout=10,
        )
    except requests.RequestException:
        return None

    if resp.status_code != 200:
        return None

    try:
        return resp.json()
    except json.JSONDecodeError:
        return None


__all__ = ["_LEVEL_NAMES", "get_api_key", "tianditu_request"]
