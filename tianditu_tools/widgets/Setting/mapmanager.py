import json
import zipfile
from pathlib import Path

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
)

from ...compat import Checked, Unchecked
from ...utils import APP_FONT, PluginConfig

ui_font = QFont()
ui_font.setFamily(APP_FONT)
ui_font.setPointSize(8)


class MapManager(QTreeWidget):
    """
    地图管理
    """

    # 分组配置：(id, 显示名称)，按显示顺序排列
    SECTION_ORDER = [
        ("tianditu_province", "天地图省级节点"),
        ("extra", "其他地图"),
    ]

    def __init__(self, map_folder: Path, parent=None):
        super().__init__(parent)
        self.map_folder = map_folder
        self.setFont(ui_font)
        self.conf = PluginConfig()
        self.setupUI()

    def setupUI(self):
        self.clear()
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setUniformRowHeights(True)
        # 设置宽度
        self.setColumnWidth(0, 350)
        self.load_map_summary()
        self.expandAll()

    def load_map_detail(self, map_id):
        mapfile_path = self.map_folder.joinpath(f"{map_id}.json")
        with open(mapfile_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_map_id_by_name(self, name):
        """通过地图名称获取 id"""
        for map_id, display_name in self.SECTION_ORDER:
            if display_name == name:
                return map_id
        return None

    def load_map_summary(self):
        for map_id, display_name in self.SECTION_ORDER:
            item = QTreeWidgetItem(self, [display_name])
            item.setSizeHint(0, QSize(160, 28))
            extra_maps_status = self.conf.get_extra_maps_status()
            map_detail = self.load_map_detail(map_id)
            section_maps_status = extra_maps_status[map_id]
            # 添加地图item
            for map_name in map_detail.keys():
                child_item = QTreeWidgetItem(item)
                child_item.setText(0, map_name)
                # 是否启用
                if map_name in section_maps_status:
                    child_item.setCheckState(0, Checked)
                else:
                    child_item.setCheckState(0, Unchecked)

            self.addTopLevelItem(item)

    def load_map_package_clicked(self):
        """
        加载地图包：选择 zip 文件，将其中的 json 文件解压到 maps 目录
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择地图包", "", "ZIP 文件 (*.zip)"
        )
        if not file_path:
            return

        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                json_files = [f for f in zf.namelist() if f.endswith(".json")]
                if not json_files:
                    QMessageBox.information(
                        self, "提示", "所选 ZIP 包中未找到 JSON 文件"
                    )
                    return
                zf.extractall(self.map_folder, members=json_files)
            names = "\n".join(sorted(json_files))
            QMessageBox.information(
                self,
                "导入成功",
                f"已导入以下地图文件：\n{names}",
            )
            self.setupUI()
        except zipfile.BadZipFile:
            QMessageBox.critical(self, "错误", "所选文件不是有效的 ZIP 文件")
        except OSError as e:
            QMessageBox.critical(self, "错误", f"加载地图包失败：{e}")

    def update_map_enable_state(self):
        top_level_item_count = self.topLevelItemCount()
        current_status = {}
        for i in range(top_level_item_count):
            top_level_item = self.topLevelItem(i)
            map_name = top_level_item.text(0)
            map_id = self.get_map_id_by_name(map_name)
            # 获取子项的数量
            child_count = top_level_item.childCount()
            # 遍历子项
            checked_item = []
            for j in range(child_count):
                child_item = top_level_item.child(j)
                if child_item.checkState(0) == 2:
                    checked_item.append(child_item.text(0))
            current_status[map_id] = checked_item
        # 保存状态
        self.conf.set_extra_maps_status(current_status)
