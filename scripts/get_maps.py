import json
from pathlib import Path
from urllib.parse import urlencode

from owslib.wmts import WebMapTileService


def get_info(wmts_url):
    result = []
    wmts = WebMapTileService(wmts_url)
    # layer_ids = list(wmts.contents)
    for layer_id in wmts.contents:
        layer = wmts.contents.get(layer_id)
        if not layer:
            continue
        title = layer.title
        img_format = layer.formats[0]
        style = list(layer.styles.keys())[0]
        tilematrixset_name = next(iter(layer.tilematrixsetlinks.keys()))
        tilematrixset = wmts.tilematrixsets.get(tilematrixset_name)
        if not tilematrixset:
            continue
        crs = tilematrixset.crs

        uri = build_qgis_wmts_uri(
            wmts_url,
            layer_id,
            style,
            tilematrixset_name,
            img_format=img_format,
            crs=crs,
        )

        result.append(
            {
                "name": title,
                "uri": uri,
            }
        )
    return result


def build_qgis_wmts_uri(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    wmts_url,
    layer_id,
    style="default",
    tilematrixset=None,
    img_format="image/png",
    crs="EPSG:3857",
):
    """
    构建QGIS WMTS图层URI
    :param wmts_url: URL
    :param layer_id: 图层名称
    :param style: 样式名称
    :param tilematrixset: 瓦片矩阵集名称（如WebMercatorQuad）
    :param img_format: 图片格式
    :param crs: 坐标参考系
    :param extra_params: 其他QGIS参数，如dpiMode=7&featureCount=10
    :return: URI字符串
    """
    params = {
        "crs": crs,
        "format": img_format,
        # "dpiMode": 7,
        # "featureCount": 10,
        "tilePixelRatio": 0,
        "layers": layer_id,
        "styles": style,
        "tileMatrixSet": tilematrixset,
        "url": wmts_url,
    }
    # 编码参数，保留特殊字符(3.44版本不能正常解析urlencode后的uri)
    query_string = urlencode(params, safe=":/")
    return query_string


tianditu_province = {
    "天地图-江苏": "https://wmts.liuxs.pro/tianditu/jiangsu",
    "天地图-广东": "https://wmts.liuxs.pro/tianditu/guangdong",
    "天地图-北京": "https://wmts.liuxs.pro/tianditu/beijing",
    "天地图-上海": "https://wmts.liuxs.pro/tianditu/shanghai",
    "天地图-湖南": "https://wmts.liuxs.pro/tianditu/hunan",
}

if __name__ == "__main__":
    cwd = Path.cwd()
    map_dir = cwd / "tianditu_tools/maps"
    map_data = {}
    for name, url in tianditu_province.items():
        print(f"Fetching {name}...")
        infos = get_info(url)
        map_data[name] = infos
    with open(map_dir / "tianditu_province.json", "w", encoding="utf-8") as f:
        json.dump(map_data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {map_dir / 'tianditu_province.json'}")
