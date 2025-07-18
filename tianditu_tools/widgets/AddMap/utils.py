from urllib.parse import quote, urlencode

from qgis.core import Qgis


def parse_referer(referer):
    if not referer:
        return ""
    # Determine the correct parameter name based on the QGIS version
    param_name = "http-header:referer" if Qgis.QGIS_VERSION_INT >= 32600 else "referer"
    return f"&{param_name}={referer}"


def get_xyz_uri(url: str, zmin: int = 0, zmax: int = 18, referer: str = "") -> str:
    """返回 XYZ Tile 地图 uri

    Args:
        url (str): 瓦片地图 url
        zmin (int, optional): z 最小值. Defaults to 0.
        zmax (int, optional): z 最大值 Defaults to 18.
        referer (str, optional): Referer. Defaults to "".

    Returns:
        str: 瓦片地图uri
    """
    # "?" 进行 URL 编码后, 在 3.34 版本上无法加载地图
    # "&" 是必须要进行 url 编码的
    url = quote(url, safe=":/?=")
    parsed_referer = parse_referer(referer)
    uri = f"type=xyz&url={url}&zmin={zmin}&zmax={zmax}{parsed_referer}"
    return uri


def get_wmts_uri(uri, referer=""):
    parsed_referer = parse_referer(referer)
    return uri + parsed_referer


def _gen_wmts_uri(crs, img_format, layers, matrix, url):
    params = {
        "crs": crs,
        "format": img_format,
        "layers": layers,
        "styles": "default",
        "tileMatrixSet": matrix,
        "tilePixelRatio": 0,
        "url": url,
    }
    query_string = urlencode(params, safe=":/")
    return query_string
