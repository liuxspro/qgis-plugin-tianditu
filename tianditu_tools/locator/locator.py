import json

import requests
from qgis.core import (
    QgsLocatorFilter,
    QgsLocatorResult,
    QgsPointXY,
    QgsProject,
)
from qgis.PyQt.QtCore import QCoreApplication

from ..qgis_utils import create_crs84_point_layer, log_message
from ..utils import PluginConfig, get_point_style


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

    def fetchResults(self, string, _context, feedback):
        keyword = string.strip()
        api_key = self._get_api_key()
        if not keyword or not api_key or feedback.isCanceled():
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

        if feedback.isCanceled() or resp.status_code != 200:
            return

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return

        suggests = data.get("suggests", [])
        if not suggests:
            return

        for index, item in enumerate(suggests):
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
            # version >=3.18
            result.userData = point
            result.score = 100 - index

            self.resultFetched.emit(result)

    @staticmethod
    def _build_post_str(keyword):
        return json.dumps(
            {
                "yingjiType": 1,
                "sourceType": 0,
                "keyWord": keyword,
                "level": 3,
                "mapBound": "-180,-90,180,90",
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
        if not isinstance(point, QgsPointXY):
            return
        name = result.displayString
        layer, feature = create_crs84_point_layer(name, point)
        layer.loadNamedStyle(get_point_style())
        QgsProject.instance().addMapLayer(layer)
        # zoom to feature
        self.iface.mapCanvas().zoomToFeatureIds(layer, [feature.id()])
        self.iface.mapCanvas().zoomScale(18056)  # 设置缩放等级, setExtent的缩放等级太大
        self.iface.mapCanvas().refresh()

    def triggerResultFromAction(self, result, _action):
        self.triggerResult(result)
