import json
import math

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDateTimeRange,
    QgsNetworkAccessManager,
    QgsProject,
)
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QDateTime
from qgis.PyQt.QtWidgets import QAction, QListWidgetItem, QTreeWidgetItem

from ...compat import (
    AlignCenter,
    DescendingOrder,
    HeaderStretch,
    NoError,
    RightDockWidgetArea,
    Ui_SdDockWidget,
    UserRole,
    exec_dialog,
)
from ...qgis_utils import add_raster_layer, push_message
from ...utils import PluginConfig, make_request
from ..icons import icons
from .token_dialog import SdTokenDialog


class SdDock(QtWidgets.QDockWidget, Ui_SdDockWidget):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.pushButton_search.clicked.connect(self.get_his_maps)
        self.init_tree_widget()
        self.conf = PluginConfig()
        self.tk = None
        self.pushButton_token.clicked.connect(self.show_token_dialog)
        self.sd_tile_data = {
            "山东省影像注记": "sdrasterpubmapdj",
            "山东省电子地图": "sdpubmap",
            "山东省影像地图": "sdrasterpubmap",
        }
        self.sd_tile_LayerId = {
            "sdrasterpubmapdj": "SDRasterPubMapDJ",
            "sdpubmap": "SDPubMap",
            "sdrasterpubmap": "SDRasterPubMap",
        }
        self.init_tk()
        self.init_list_widget()

    def init_tk(self):
        self.tk = self.conf.get_value("Other/sd_tk") or ""
        has_tk = bool(self.tk)
        self.pushButton_search.setEnabled(has_tk)
        self.listWidget.setEnabled(has_tk)
        if has_tk:
            self.set_token_status("Token 已配置")
        else:
            self.set_token_status("未配置 Token", is_warning=True)

    def set_token_status(self, text: str, is_warning: bool = False):
        color = "#cf222e" if is_warning else "#808080"
        self.label_token_status.setStyleSheet(f"color: {color};")
        self.label_token_status.setText(text)

    def show_token_dialog(self):
        dialog = SdTokenDialog(parent=self)
        try:
            exec_dialog(dialog)
        finally:
            dialog.deleteLater()
        self.init_tk()

    def init_tree_widget(self):
        header = self.treeWidget.header()
        # 名称列自适应宽度，时间与分辨率列固定
        header.setSectionResizeMode(0, HeaderStretch)
        header.setStretchLastSection(False)
        self.treeWidget.setColumnWidth(1, 96)
        self.treeWidget.setColumnWidth(2, 96)
        # 连接双击事件
        self.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)

    def init_list_widget(self):
        self.listWidget.adjustSize()
        self.listWidget.itemDoubleClicked.connect(self.on_listitem_double_clicked)

        for name in self.sd_tile_data:
            item = QListWidgetItem(name)
            self.listWidget.addItem(item)

    def on_listitem_double_clicked(self, item):
        item_name = item.text()
        t_id = self.sd_tile_data[item_name]
        cap_url = f"https://service.sdmap.gov.cn/tileservice/{t_id}?tk%3D{self.tk}"
        cap_url += "%26Service%3DWMTS%26Request%3DGetCapabilities"

        uri = f"crs=EPSG:4490&dpiMode=7&format=image/jpeg&layers={self.sd_tile_LayerId[t_id]}"
        if item_name == "山东省影像注记":
            uri += (
                f"&styles=default&tileMatrixSet=rasterdj&tilePixelRatio=0&url={cap_url}"
            )
        else:
            uri += (
                f"&styles=default&tileMatrixSet=raster&tilePixelRatio=0&url={cap_url}"
            )
        add_raster_layer(uri, item_name)

    def get_center_point(self):
        canvas = self.iface.mapCanvas()
        center_point = canvas.center()
        source_crs = canvas.mapSettings().destinationCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            source_crs, target_crs, QgsProject.instance()
        )
        center_point_4326 = transform.transform(center_point)
        return center_point_4326.x(), center_point_4326.y()

    def get_zoom_level(self):
        canvas = self.iface.mapCanvas()
        current_scale = canvas.scale()
        scale_list = [
            2 * math.pi * 6378137 / (256 * pow(2, x) * 0.00028) for x in range(22)
        ]
        level = min(
            range(len(scale_list)), key=lambda i: abs(scale_list[i] - current_scale)
        )
        return level

    def set_his_status(self, text: str):
        self.label_his_status.setText(text)

    def get_his_maps(self):
        point = (117.7, 36)
        level = 7
        # 是否根据画布范围查询
        if self.checkBox.isChecked():
            point = self.get_center_point()
            level = self.get_zoom_level()

        self.set_his_status("正在查询…")
        self.pushButton_search.setEnabled(False)
        self.pushButton_search.setText("查询中…")
        QtWidgets.QApplication.processEvents()
        try:
            self.query_his_maps(point, level)
        finally:
            self.pushButton_search.setText("查询历史影像")
            self.pushButton_search.setEnabled(bool(self.tk))

    def query_his_maps(self, point, level):
        network_manager = QgsNetworkAccessManager.instance()

        url = "https://service.sdmap.gov.cn/imgmeta?"
        url += f"wktpoint=POINT({point[0]} {point[1]})&level={level}&tk={self.tk}"
        request = make_request(url)
        reply = network_manager.blockingGet(request)

        message_title = "天地图·山东 - 查询出错"
        if reply.error() != NoError:
            self.set_his_status("查询请求失败，请检查网络连接")
            push_message(self.iface, message_title, reply.errorString())
            return

        try:
            raw_data = json.loads(reply.content().data())
        except json.decoder.JSONDecodeError:
            raw_data = None

        if not isinstance(raw_data, list):
            self.treeWidget.clear()
            if level > 18:
                self.set_his_status("缩放层级不能超过 18 级")
                push_message(self.iface, message_title, "缩放层级不能超过18级")
            else:
                self.set_his_status("未查询到数据，请检查画布中心是否在山东省境内")
                push_message(
                    self.iface,
                    message_title,
                    "请检查画布中心是否在山东省境内！",
                )
            return

        # 筛选出历史影像
        # tileservice/sdrasterpubmap 添加方式不同
        his_data = [d for d in raw_data if "hisimage" in str(d.get("url", ""))]
        sorted_data = sorted(his_data, key=lambda x: x.get("st", ""))
        self.add_item(sorted_data)
        # 默认按照时间降序排序
        self.treeWidget.sortByColumn(1, DescendingOrder)

        if sorted_data:
            self.set_his_status(f"共 {len(sorted_data)} 条影像，双击条目添加到底图")
        else:
            self.set_his_status("当前范围没有历史影像")

    def add_item(self, map_data):
        # 批量插入时先关闭排序，避免条目在插入过程中反复重排
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.clear()  # 先清空 item
        for m in map_data:
            item = QTreeWidgetItem(self.treeWidget)
            item.setText(0, m.get("name", ""))
            item.setText(1, str(m.get("st", "")))
            item.setText(2, str(m.get("reso", "")))
            # url、el 不作为列展示，随条目一起保存
            item.setData(
                0,
                UserRole,
                {"url": m.get("url", ""), "el": str(m.get("el", ""))},
            )
            item.setTextAlignment(1, AlignCenter)
            item.setTextAlignment(2, AlignCenter)
        self.treeWidget.setSortingEnabled(True)

    def on_item_double_clicked(self, item):
        """
        处理双击事件
        :param item: 被双击的 QTreeWidgetItem
        """
        data = item.data(0, UserRole) or {}
        url = data.get("url", "")
        el = data.get("el", "")
        if not url:
            return

        name = f"山东 - {item.text(0)}"
        mapid = url.split("/")[-1]
        # 为山东天地图历史影像写了一个简单的 WMTS Capabilities 生成服务
        # 源代码见 https://github.com/liuxspro/wmts/blob/main/src/server.ts
        his_wmts_server = "https://wmts.liuxs.pro/"
        cap_url = f"{his_wmts_server}tianditu/sdhis/{mapid}/{el}?tk%3D{self.tk}"
        uri = f"crs=EPSG:4490&format=image/jpeg&layers={mapid}"
        uri += f"&styles=default&tileMatrixSet=CGCS2000QuadF3T{el}&url={cap_url}"

        layer = add_raster_layer(uri, name)
        if layer is None:
            self.set_his_status("图层加载失败，请检查 Token 是否有效")
            return

        # 设置图层时态 (3.22 版本以上)
        current_qgis_version = Qgis.QGIS_VERSION_INT
        if current_qgis_version <= 32200:
            return

        date_str = item.text(1)
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = 1
        if len(date_str) > 6:
            day = int(date_str[6:])
        temporal_props = layer.temporalProperties()
        temporal_props.setMode(
            Qgis.RasterTemporalMode.FixedTemporalRange
        )  # 3.22 版本以上
        start_date = QDateTime(year, month, day, 0, 0, 0)
        end_date = QDateTime(year, month, day, 23, 59, 59)
        date_range = QgsDateTimeRange(start_date, end_date)
        temporal_props.setFixedTemporalRange(date_range)
        temporal_props.setIsActive(True)


class SdAction(QAction):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.dock = SdDock(iface)
        self.setIcon(icons["map"])
        self.setText("天地图·山东 ↗︎")
        self.triggered.connect(self.open_dock)

    def open_dock(self):
        # https://qgis.org/pyqgis/master/gui/QgisInterface.html#qgis.gui.QgisInterface.addTabifiedDockWidget
        self.iface.addTabifiedDockWidget(
            RightDockWidgetArea, self.dock, ["sd"], raiseTab=True
        )
