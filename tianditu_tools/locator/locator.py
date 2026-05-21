import json

import requests
from qgis.core import (
    QgsLocatorFilter,
    QgsLocatorResult,
    QgsPointXY,
    QgsFeature,
    QgsGeometry,
    QgsVectorLayer,
    QgsProject,
)

from qgis.PyQt.QtCore import QCoreApplication


from ..utils import PluginConfig
from ..qgis_utils import log_message

# from ..widgets.icons import icons


def create_point_layer(name: str, point: QgsPointXY, crs: str):
    layer = QgsVectorLayer(f"Point?crs={crs}&field=Name:string", name, "memory")
    pr = layer.dataProvider()
    point_feature = QgsFeature()
    point_feature.setGeometry(QgsGeometry.fromPointXY(point))
    point_feature.setAttributes([name])
    pr.addFeature(point_feature)
    return layer, point_feature


class TDTGeocoderFilter(QgsLocatorFilter):
    """天地图地名搜索 Locator Filter"""

    BASE_URL = "https://api.tianditu.gov.cn/v2/search"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.conf = PluginConfig()
        self._marker = None

    def clone(self):
        return TDTGeocoderFilter(self.iface)

    def name(self):
        return "TianDiTu Geocoder"

    def displayName(self):
        return QCoreApplication.translate("TDTGeocoder", "天地图地名搜索")

    def prefix(self):
        return "tdt"

    def useWithoutPrefix(self):
        return True

    def hasFeatures(self):
        return True

    def clearPreviousResults(self):
        super().clearPreviousResults()

    def fetchResults(self, string, context, feedback):
        keyword = string.strip()
        if not keyword:
            return

        api_key = self._get_api_key()
        if not api_key:
            return

        if feedback.isCanceled():
            return

        post_str = self._build_post_str(keyword)
        log_message(f"API Search: {keyword}")
        try:
            resp = requests.get(
                self.BASE_URL,
                params={"type": "query", "postStr": post_str, "tk": api_key},
                headers={
                    "User-Agent": "Mozilla/5.0 QGIS/32400/Windows 10 Version 2009",
                    "Referer": "https://www.tianditu.gov.cn/",
                },
                timeout=10,
            )
        except requests.RequestException:
            return

        if feedback.isCanceled():
            return

        if resp.status_code != 200:
            return

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return

        suggests = data.get("suggests", [])
        if not suggests:
            return

        for item in suggests:
            if feedback.isCanceled():
                return

            lonlat = item.get("lonlat", "")
            if not lonlat:
                continue

            try:
                lon, lat = lonlat.split(",")
                point = QgsPointXY(float(lon), float(lat))
            except (ValueError, TypeError):
                continue

            result = QgsLocatorResult()
            result.filter = self
            result.displayString = item.get("name", "")
            result.description = item.get("address", "")
            result.userData = point
            result.score = 0
            # result.icon = icons["map"]

            self.resultFetched.emit(result)

    @staticmethod
    def _build_post_str(keyword):
        return json.dumps(
            {
                "yingjiType": 1,
                "sourceType": 0,
                "keyWord": keyword,
                "level": 3,
                "mapBound": "22.551757812499574,8.681744001784637,179.99,44.850206918799245",
                "queryType": "4",
                "start": 0,
                "count": 10,
                "queryTerminal": 10000,
                "webService": True,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def _get_api_key(self):
        if self.conf.get_bool_value("Tianditu/random_key"):
            return self.conf.get_random_key()
        key = self.conf.get_key()
        if not key:
            key = self.conf.get_value("Tianditu/keyList")
            if key:
                keys = key.split(",")
                if keys:
                    key = keys[0].strip()
        return key or ""

    def triggerResult(self, result):
        # https://qgis.org/pyqgis/master/core/QgsLocatorResult.html
        point = result.userData

        print(result)
        if not isinstance(point, QgsPointXY):
            return
        name = result.displayString
        raw_layer, feature = create_point_layer(name, point, "EPSG:4326")
        QgsProject.instance().addMapLayer(raw_layer)
        raw_layer.selectByIds([feature.id()])
        self.canvas.zoomToSelected()
        raw_layer.removeSelection()

    def triggerResultFromAction(self, result, action):
        self.triggerResult(result)
