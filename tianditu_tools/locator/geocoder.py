import json

from qgis.core import (
    QgsLocatorFilter,
    QgsLocatorResult,
    QgsPointXY,
    QgsProject,
)
from qgis.PyQt.QtCore import QCoreApplication

from ..qgis_utils import create_crs84_point_layer, log_message
from ..utils import PluginConfig, get_point_style
from ..widgets.icons import icons
from ._utils import get_api_key, tianditu_request


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
        return QCoreApplication.translate("TDTGeocoder", "天地图-地名搜索")

    def prefix(self):
        return "tdt"

    def useWithoutPrefix(self):
        return True

    def fetchResults(self, string, _context, feedback):
        keyword = string.strip()
        api_key = self._get_api_key()
        if not keyword or not api_key or feedback.isCanceled():
            return

        post_str = self._build_post_str(keyword)
        log_message(f"API Search: {keyword}")
        data = tianditu_request(
            self.BASE_URL,
            {"type": "query", "postStr": post_str, "tk": api_key},
        )
        if not data or feedback.isCanceled():
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
            result.icon = icons["point"]
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
        return get_api_key(self.conf)

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
        self.iface.mapCanvas().zoomScale(18056)  # ���÷Ŵȼ�, setExtent�ķŴȼ�̫��
        self.iface.mapCanvas().refresh()

    def triggerResultFromAction(self, result, _action):
        self.triggerResult(result)


__all__ = ["TDTGeocoderFilter"]
