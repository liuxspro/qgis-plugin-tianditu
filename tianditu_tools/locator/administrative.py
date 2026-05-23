import json

import requests
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsLocatorFilter,
    QgsLocatorResult,
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from ..qgis_utils import log_message
from ..utils import PluginConfig
from ..widgets.icons import icons
from ._utils import _LEVEL_NAMES, get_api_key


class TDTAdministrativeFilter(QgsLocatorFilter):
    """天地图行政区划搜索 Locator Filter"""

    BASE_URL = "https://api.tianditu.gov.cn/v2/administrative"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.conf = PluginConfig()

    def clone(self):
        return TDTAdministrativeFilter(self.iface)

    def name(self):
        return "TianDiTu Administrative Divisions"

    def displayName(self):
        return QCoreApplication.translate("TDTAdministrative", "天地图-行政区划搜索")

    def prefix(self):
        return "tdt-adm"

    def useWithoutPrefix(self):
        return True

    def fetchResults(self, string, _context, feedback):
        keyword = string.strip()
        api_key = get_api_key(self.conf)
        if not keyword or not api_key or feedback.isCanceled():
            return

        log_message(f"Admin Search: {keyword}")
        try:
            resp = requests.get(
                self.BASE_URL,
                params={
                    "keyword": keyword,
                    "childLevel": "0",
                    "extensions": "true",
                    "tk": api_key,
                },
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

        if data.get("status") != 200:
            return

        districts = data.get("data", {}).get("district", [])
        if not districts:
            # 尝试使用 suggestion 字段（模糊匹配且只有一条精确结果时）
            suggestion = data.get("data", {}).get("suggestion", [])
            if not suggestion:
                return
            for sug in suggestion:
                if feedback.isCanceled():
                    return
                sug_name = sug.get("name", "") if isinstance(sug, dict) else str(sug)
                sug_gb = sug.get("gb", "") if isinstance(sug, dict) else ""
                if not sug_name:
                    continue
                result = QgsLocatorResult()
                result.filter = self
                result.displayString = sug_name
                result.description = QCoreApplication.translate(
                    "TDTAdministrative", "建议搜索 | 双击查询行政区划"
                )
                result.userData = sug_gb
                result.icon = icons["polygon"]
                result.score = 50
                self.resultFetched.emit(result)
            return

        for item in districts:
            if feedback.isCanceled():
                return

            boundary = item.get("boundary", "")
            if not boundary:
                continue

            level = item.get("level", 0)
            level_name = _LEVEL_NAMES.get(level, f"Level {level}")
            gb_code = item.get("gb", "")

            result = QgsLocatorResult()
            result.filter = self
            result.displayString = item.get("name", "")
            result.description = (
                f"{level_name} | GB: {gb_code}" if gb_code else level_name
            )
            result.icon = icons["polygon"]
            result.userData = boundary
            result.score = 100 - level
            self.resultFetched.emit(result)

    def triggerResult(self, result):
        user_data = result.userData
        if not isinstance(user_data, str) or not user_data:
            return

        name = result.displayString

        # 处理 GB 编码：二次请求获取边界数据
        if user_data.isdigit():
            user_data = self._fetch_boundary_by_gb(user_data, name)
            if not user_data:
                return

        layer = QgsVectorLayer(
            "Polygon?crs=EPSG:4326&field=Name:string", name, "memory"
        )
        pr = layer.dataProvider()
        feature = QgsFeature()
        geom = QgsGeometry.fromWkt(user_data)
        if geom.isNull() or not geom.isGeosValid():
            log_message(f"Invalid boundary WKT for {name}")
            return
        feature.setGeometry(geom)
        feature.setAttributes([name])
        pr.addFeature(feature)
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)
        self.iface.mapCanvas().zoomToFeatureIds(layer, [feature.id()])
        self.iface.mapCanvas().refresh()

    @staticmethod
    def _fetch_boundary_by_gb(gb_code, name):
        """根据 GB 编码二次请求行政区划边界 WKT"""
        api_key = get_api_key(PluginConfig())
        if not api_key:
            log_message(f"Cannot fetch boundary for {name}: no API key")
            return ""
        try:
            resp = requests.get(
                TDTAdministrativeFilter.BASE_URL,
                params={
                    "keyword": gb_code,
                    "childLevel": "0",
                    "extensions": "true",
                    "tk": api_key,
                },
                headers={
                    "User-Agent": "Mozilla/5.0 QGIS/32400/Windows 10 Version 2009",
                    "Referer": "https://www.tianditu.gov.cn/",
                },
                timeout=10,
            )
        except requests.RequestException as e:
            log_message(f"Request failed for {name}: {e}")
            return ""

        if resp.status_code != 200:
            return ""

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return ""

        if data.get("status") != 200:
            return ""

        districts = data.get("data", {}).get("district", [])
        if not districts:
            return ""

        boundary = districts[0].get("boundary", "")
        if not boundary:
            log_message(f"No boundary data for {name} (GB: {gb_code})")
        return boundary

    def triggerResultFromAction(self, result, _action):
        self.triggerResult(result)


__all__ = ["TDTAdministrativeFilter"]
