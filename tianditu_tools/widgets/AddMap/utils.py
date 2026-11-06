from urllib.parse import quote

from qgis.core import Qgis

# 天地图 EPSG:4490 瓦片使用的坐标系与瓦片矩阵集
WMTS_C_CRS = "EPSG:4490"
WMTS_C_MATRIX_SET = "CGCS2000Quad"


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


def get_local_wmts_uri(
    caps_file,
    layers: str,
    img_format: str = "image/png",
    crs: str = WMTS_C_CRS,
    matrix_set: str = WMTS_C_MATRIX_SET,
) -> str:
    """返回基于本地 WMTS capabilities 文件的图层 uri

    caps 文件名必须包含 WMTSCapabilities.xml，QGIS 靠它判断这是一个 WMTS
    （isUrlForWMTS），否则会追加 SERVICE=WMS&REQUEST=GetCapabilities。

    Args:
        caps_file (Path): 本地 capabilities 文件
        layers (str): capabilities 中的图层标识
        img_format (str): 需与图层声明的 Format 一致，QGIS 用它匹配 ResourceURL 模板
        crs (str): 坐标系
        matrix_set (str): 瓦片矩阵集标识

    Returns:
        str: 栅格图层 uri
    """
    params = [
        ("crs", crs),
        ("format", img_format),
        ("layers", layers),
        ("styles", "default"),
        ("tileMatrixSet", matrix_set),
        ("tilePixelRatio", "0"),
        # 只能局部编码："&" 必须编码为 %26，":" 与 "/" 保留以便 QGIS 识别 file:// 路径
        ("url", caps_file.as_uri()),
    ]
    return "&".join(f"{name}={quote(value, safe=':/?=')}" for name, value in params)
