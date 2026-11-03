import json
import zipfile
from pathlib import Path

from qgis.PyQt.QtCore import QSize, pyqtSignal
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
)

from ...compat import Checked, PartiallyChecked, Unchecked, UserRole
from ...qgis_utils import log_message
from ...utils import APP_FONT, PluginConfig

ui_font = QFont()
ui_font.setFamily(APP_FONT)
ui_font.setPointSize(8)


class MapManager(QTreeWidget):
    """
    地图管理：按分组列出可用地图源，并记录哪些显示在「添加地图」菜单中
    """

    # 分组配置：(id, 显示名称)，按显示顺序排列
    SECTION_ORDER = [
        ("tianditu_province", "天地图省级节点"),
        ("extra", "其他地图"),
    ]

    counts_changed = pyqtSignal(int, int)

    def __init__(self, map_folder: Path, parent=None):
        super().__init__(parent)
        self.map_folder = map_folder
        self.conf = PluginConfig()
        self._updating = False
        self.setFont(ui_font)
        self.setup_ui()
        self.itemChanged.connect(self._on_item_changed)

    def setup_ui(self):
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setUniformRowHeights(True)
        self.setColumnWidth(0, 350)
        self.reload()

    def reload(self):
        """从配置重新加载地图列表"""
        status = self.conf.get_extra_maps_status()
        self._updating = True
        try:
            self.clear()
            for map_id, display_name in self.SECTION_ORDER:
                section = QTreeWidgetItem(self, [display_name])
                section.setData(0, UserRole, map_id)
                section.setSizeHint(0, QSize(160, 28))
                section.setExpanded(True)
                enabled_maps = status.get(map_id, [])
                for map_name in self.load_map_detail(map_id):
                    child = QTreeWidgetItem(section)
                    child.setText(0, map_name)
                    child.setData(0, UserRole, map_name)
                    child.setCheckState(
                        0, Checked if map_name in enabled_maps else Unchecked
                    )
                self._update_section_state(section)
        finally:
            self._updating = False
        self.expandAll()
        self._emit_counts()

    def load_map_detail(self, map_id):
        mapfile_path = self.map_folder.joinpath(f"{map_id}.json")
        try:
            with open(mapfile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            log_message(f"读取地图文件失败 {mapfile_path}: {exc}")
            return {}

    def save_state(self):
        """保存各分组启用状态"""
        status = {}
        for i in range(self.topLevelItemCount()):
            section = self.topLevelItem(i)
            map_id = section.data(0, UserRole)
            status[map_id] = [
                section.child(j).text(0)
                for j in range(section.childCount())
                if section.child(j).checkState(0) == Checked
            ]
        self.conf.set_extra_maps_status(status)

    def counts(self):
        """返回 (已启用数量, 总数)"""
        checked = 0
        total = 0
        for i in range(self.topLevelItemCount()):
            section = self.topLevelItem(i)
            for j in range(section.childCount()):
                total += 1
                if section.child(j).checkState(0) == Checked:
                    checked += 1
        return checked, total

    def apply_filter(self, text: str):
        """按名称筛选地图，无匹配项的分组一并隐藏"""
        keyword = text.strip().lower()
        for i in range(self.topLevelItemCount()):
            section = self.topLevelItem(i)
            matched_count = 0
            for j in range(section.childCount()):
                child = section.child(j)
                matched = keyword in child.text(0).lower()
                child.setHidden(not matched)
                matched_count += matched
            section.setHidden(matched_count == 0)
        if keyword:
            self.expandAll()

    def set_all_checked(self, checked: bool):
        """全选 / 全不选（仅作用于当前可见项）"""
        state = Checked if checked else Unchecked
        self._updating = True
        try:
            for i in range(self.topLevelItemCount()):
                section = self.topLevelItem(i)
                if section.isHidden():
                    continue
                for j in range(section.childCount()):
                    child = section.child(j)
                    if not child.isHidden():
                        child.setCheckState(0, state)
                self._update_section_state(section)
        finally:
            self._updating = False
        self._emit_counts()

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
                json_files = [
                    name
                    for name in zf.namelist()
                    if name.lower().endswith(".json") and self._is_safe_zip_name(name)
                ]
                if not json_files:
                    QMessageBox.information(
                        self, "提示", "所选 ZIP 包中未找到 JSON 文件"
                    )
                    return
                zf.extractall(self.map_folder, members=json_files)
            names = "\n".join(sorted(Path(name).name for name in json_files))
            QMessageBox.information(
                self,
                "导入成功",
                f"已导入以下地图文件：\n{names}",
            )
            self.reload()
        except zipfile.BadZipFile:
            QMessageBox.critical(self, "错误", "所选文件不是有效的 ZIP 文件")
        except OSError as e:
            QMessageBox.critical(self, "错误", f"加载地图包失败：{e}")

    @staticmethod
    def _is_safe_zip_name(name: str) -> bool:
        """只允许解压 maps 目录下的单个文件，避免 zip 路径穿越"""
        return not (
            name.startswith(("/", "\\")) or ".." in name or "/" in name or "\\" in name
        )

    def _update_section_state(self, section):
        total = section.childCount()
        checked = sum(
            1 for j in range(total) if section.child(j).checkState(0) == Checked
        )
        if checked == 0:
            state = Unchecked
        elif checked == total:
            state = Checked
        else:
            state = PartiallyChecked
        section.setCheckState(0, state)

    def _on_item_changed(self, item, column):
        if column != 0 or self._updating:
            return
        self._updating = True
        try:
            if item.parent() is None:
                state = item.checkState(0)
                if state != PartiallyChecked:
                    for j in range(item.childCount()):
                        item.child(j).setCheckState(0, state)
            else:
                for i in range(self.topLevelItemCount()):
                    self._update_section_state(self.topLevelItem(i))
        finally:
            self._updating = False
        self._emit_counts()

    def _emit_counts(self):
        checked, total = self.counts()
        self.counts_changed.emit(checked, total)
