import json
import math

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QAction, QTreeWidgetItem, QListWidgetItem
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.core import QgsNetworkAccessManager

from ..icons import icons
from ...compat import (
    Ui_SdDockWidget,
    RightDockWidgetArea,
    NoError,
    AlignCenter,
    DescendingOrder,
)
from ...qgis_utils import add_raster_layer, push_message
from ...utils import PluginConfig, make_request


class SdDock(QtWidgets.QDockWidget, Ui_SdDockWidget):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.pushButton_search.clicked.connect(self.get_his_maps)
        self.init_tree_widget()
        self.conf = PluginConfig()
        self.tk = None
        self.pushButton_save.clicked.connect(self.save_tk)
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
        self.tk = self.conf.get_value("Other/sd_tk")
        if self.tk is None:
            self.pushButton_search.setEnabled(False)
            self.listWidget.setEnabled(False)
        else:
            self.mLineEdit_sdtk.setText(self.tk)

    def init_tree_widget(self):
        self.treeWidget.setColumnWidth(0, 160)
        self.treeWidget.setColumnWidth(1, 100)
        self.treeWidget.setColumnWidth(2, 60)
        # 连接双击事件
        self.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        # 启用排序功能
        self.treeWidget.setSortingEnabled(True)
        # 隐藏 url 和 el 列
        self.treeWidget.header().hideSection(3)
        self.treeWidget.header().hideSection(4)

    def save_tk(self):
        tk = self.mLineEdit_sdtk.text()
        if tk != "":
            self.conf.set_value("Other/sd_tk", tk)
            self.init_tk()
            self.pushButton_search.setEnabled(True)
            self.listWidget.setEnabled(True)

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

    def get_his_maps(self):
        point = (117.7, 36)
        level = 7
        # 是否根据画布范围查询
        if self.checkBox.isChecked():
            point = self.get_center_point()
            level = self.get_zoom_level()

        # 构建查询
        network_manager = QgsNetworkAccessManager.instance()

        url = "https://service.sdmap.gov.cn/imgmeta?"
        url += f"wktpoint=POINT({point[0]} {point[1]})&level={level}&tk={self.tk}"
        request = make_request(url)
        reply = network_manager.blockingGet(request)
        if reply.error() == NoError:
            try:
                raw_data = json.loads(reply.content().data())
            except json.decoder.JSONDecodeError:
                raw_data = []
                message_title = "天地图·山东 - 查询出错"
                if level > 18:
                    push_message(self.iface, message_title, "缩放层级不能超过18级")
                else:
                    push_message(
                        self.iface,
                        message_title,
                        "请检查画布中心是否在山东省境内！",
                    )

            # 筛选出历史影像
            # tileservice/sdrasterpubmap 添加方式不同
            his_data = [d for d in raw_data if "hisimage" in d["url"]]
            sorted_data = sorted(his_data, key=lambda x: x["st"])
            self.add_item(sorted_data)
        # 默认按照时间降序排序
        self.treeWidget.sortByColumn(1, DescendingOrder)

    def add_item(self, map_data):
        self.treeWidget.clear()  # 先清空 item
        for m in map_data:
            item = QTreeWidgetItem(self.treeWidget)
            item.setText(0, m.get("name", ""))
            item.setText(1, str(m["st"]))
            item.setText(2, str(m["reso"]))
            item.setText(3, m["url"])
            item.setText(4, str(m["el"]))
            item.setTextAlignment(0, AlignCenter)
            item.setTextAlignment(1, AlignCenter)
            item.setTextAlignment(2, AlignCenter)

    def on_item_double_clicked(self, item):
        """
        处理双击事件
        :param item: 被双击的 QTreeWidgetItem
        """
        name = f"山东 - {item.text(0)}"
        url = item.text(3)
        el = item.text(4)

        mapid = url.split("/")[-1]
        # 为山东天地图历史影像写了一个简单的 WMTS Capabilities 生成服务
        # 源代码见 https://github.com/liuxspro/wmts/blob/main/src/server.ts
        his_wmts_server = "https://wmts.liuxs.pro/"
        cap_url = f"{his_wmts_server}tianditu/sdhis/{mapid}/{el}?tk%3D{self.tk}"
        uri = f"crs=EPSG:4490&format=image/jpeg&layers={mapid}"
        uri += f"&styles=default&tileMatrixSet=CGCS2000QuadF3T{el}&url={cap_url}"

        add_raster_layer(uri, name)


class SdAction(QAction):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.iface = iface
        self.dock = SdDock(iface)
        self.setIcon(icons["map"])
        self.setText("天地图·山东")
        self.triggered.connect(self.open_dock)

    def open_dock(self):
        # https://qgis.org/pyqgis/master/gui/QgisInterface.html#qgis.gui.QgisInterface.addTabifiedDockWidget
        self.iface.addTabifiedDockWidget(
            RightDockWidgetArea, self.dock, ["sd"], raiseTab=True
        )
