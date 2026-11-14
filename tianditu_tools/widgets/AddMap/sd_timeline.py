import json

from qgis.core import QgsNetworkAccessManager, QgsProject
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QTimer

from ...compat import NoError, Ui_SdTimelineDock
from ...qgis_utils import create_raster_layer
from ...utils import PluginConfig, make_request
from .timeline import TimelineBar
from .utils import canvas_center_lonlat, canvas_zoom_level, get_sd_his_uri

REFRESH_DELAY_MS = 800
MAX_QUERY_LEVEL = 18


class SdTimelineDock(QtWidgets.QDockWidget, Ui_SdTimelineDock):
    """画布底部的历史影像时间轴，画布移动停下后自动按画布中心查询"""

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.conf = PluginConfig()
        self._reply = None
        self._last_key = None
        self._layer = None

        self.setupUi(self)
        self.timeline_bar = TimelineBar()
        self.verticalLayout_timeline.addWidget(self.timeline_bar)
        self.label_timeline_current.setStyleSheet(
            f"color: {TimelineBar.ACCENT_COLOR.name()};"
        )

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(REFRESH_DELAY_MS)
        self._timer.timeout.connect(self.refresh)

        self.timeline_bar.dateChanged.connect(self._apply_item)
        self.pushButton_prev.clicked.connect(self._previous_item)
        self.pushButton_next.clicked.connect(self._next_item)
        iface.mapCanvas().extentsChanged.connect(self._schedule_refresh)
        self.visibilityChanged.connect(self._on_visibility_changed)
        self._update_step_buttons()

    @property
    def tk(self):
        return self.conf.get_value("Other/sd_tk") or ""

    # ---------- 查询调度 ----------

    def _on_visibility_changed(self, visible):
        if visible:
            self.refresh(force=True)
        else:
            self._timer.stop()

    def _schedule_refresh(self):
        if self.isVisible():
            self._timer.start()

    def refresh(self, force=False):
        token = self.tk
        if not token:
            self.set_status("未配置 Token，请先在「天地图·山东」面板中设置")
            self.timeline_bar.clear()
            self._apply_item(None)
            self._last_key = None
            return

        point = canvas_center_lonlat(self.iface)
        level = canvas_zoom_level(self.iface)
        key = (round(point[0], 4), round(point[1], 4), level)
        if not force and key == self._last_key:
            return
        if level > MAX_QUERY_LEVEL:
            self.set_status(
                f"当前缩放级别 {level} 超过 {MAX_QUERY_LEVEL} 级，请放大后再试"
            )
            return

        self._last_key = key
        self.set_status("正在查询历史影像…")
        url = "https://service.sdmap.gov.cn/imgmeta?"
        url += f"wktpoint=POINT({point[0]} {point[1]})&level={level}&tk={token}"
        reply = QgsNetworkAccessManager.instance().get(make_request(url))
        self._reply = reply
        reply.finished.connect(self._on_reply_finished)

    def _on_reply_finished(self):
        reply = self.sender()
        if reply is not self._reply:
            reply.deleteLater()
            return
        self._reply = None

        if reply.error() != NoError:
            self.set_status(f"查询失败：{reply.errorString()}")
            reply.deleteLater()
            return

        try:
            data = json.loads(str(reply.readAll(), "utf-8", "ignore"))
        except json.decoder.JSONDecodeError:
            data = None
        reply.deleteLater()

        if not isinstance(data, list):
            self.timeline_bar.clear()
            self._apply_item(None)
            self.set_status("查询出错，请检查画布中心是否在山东省境内")
            return

        his_data = [d for d in data if "hisimage" in str(d.get("url", ""))]
        his_data.sort(key=lambda d: str(d.get("st", "")))
        self.timeline_bar.set_dates(his_data)

        lon, lat, level = self._last_key
        if his_data:
            self.set_status(
                f"画布中心 {lon:.4f}, {lat:.4f} · {level} 级 · {len(his_data)} 档影像"
            )
        else:
            self.set_status("当前画布中心附近没有历史影像")
        self._apply_item(self.timeline_bar.current_item())

    # ---------- 档期与图层 ----------

    def _apply_item(self, item):
        self._update_step_buttons()
        if not item:
            self.label_timeline_current.clear()
            return
        self.label_timeline_current.setText(self._describe(item))
        self._show_layer(item)

    def _previous_item(self):
        self.timeline_bar.step(-1)

    def _next_item(self):
        self.timeline_bar.step(1)

    def _update_step_buttons(self):
        index = self.timeline_bar.current_index()
        count = self.timeline_bar.count()
        self.pushButton_prev.setEnabled(index > 0)
        self.pushButton_next.setEnabled(0 <= index < count - 1)

    @staticmethod
    def _describe(item):
        parts = [f"当前：{_format_st(str(item.get('st', '')))}"]
        if item.get("reso"):
            parts.append(f"{item['reso']} m")
        return " · ".join(parts)

    def _show_layer(self, item):
        """只保留一个影像图层，切换档期时替换它，避免图层树越堆越多"""
        url = str(item.get("url", ""))
        el = str(item.get("el", ""))
        if not url:
            return
        mapid = url.rsplit("/", maxsplit=1)[-1]
        # 为山东天地图历史影像写了一个简单的 WMTS Capabilities 生成服务
        # 源代码见 https://github.com/liuxspro/wmts/blob/main/src/server.ts
        uri = get_sd_his_uri(self.tk, mapid, el)

        old_layer = self._layer
        if old_layer is not None:
            try:
                if old_layer.source() == uri:
                    _set_layer_visible(old_layer)
                    return
            except RuntimeError:  # 用户已在图层树中删除该图层
                self._layer = None
                old_layer = None

        name = f"山东 - {item.get('name') or mapid}"
        layer = create_raster_layer(uri, name)
        if layer is None:
            self.set_status("图层加载失败，请检查 Token 是否有效")
            return
        if old_layer is not None:
            QgsProject.instance().removeMapLayer(old_layer.id())
        QgsProject.instance().addMapLayer(layer)
        self._layer = layer

    def set_status(self, text):
        self.label_timeline_status.setText(text)

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)


def _format_st(value: str) -> str:
    """imgmeta 返回的 201304 形式的日期 -> 2013-04"""
    if len(value) >= 6:
        return f"{value[:4]}-{value[4:6]}"
    return value


def _set_layer_visible(layer):
    """setItemVisibilityChecked 在 QgsLayerTreeNode 上，而不是 QgsMapLayer 上"""
    node = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
    if node is not None:
        node.setItemVisibilityChecked(True)
