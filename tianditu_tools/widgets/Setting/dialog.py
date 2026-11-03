from qgis.core import QgsApplication
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QSize, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QFont, QIcon
from qgis.PyQt.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QToolButton

from ...compat import (
    AlignCenter,
    ButtonYes,
    HeaderStretch,
    ModeClipboard,
    MonospaceStyleHint,
    NoEditTriggers,
    NoSelection,
    PlainText,
    Ui_SettingDialog,
    UserRole,
    exec_dialog,
)
from ...utils import SUBDOMAINS, PluginConfig
from ..icons import icons
from ..MapManager import MapManagerDialog
from .keyutils import KEY_LENGTH, check_key_format, mask_key
from .verifier import KeyVerifier

STATUS_COLORS = {
    "info": "#808080",
    "success": "#1a7f37",
    "error": "#cf222e",
}
STATUS_TIMEOUT_MS = 3000


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    """天地图设置：Key 与 服务节点"""

    maps_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.conf = PluginConfig()
        self.verifier = KeyVerifier(self)
        self._loading = False
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._clear_status)

        self.setupUi(self)
        self.info_status.setTextFormat(PlainText)
        self._setup_status_area()
        self._setup_key_table()
        self._init_subdomain()
        self._init_toggles()
        self._refresh_key_list()
        self._connect_signals()
        self._update_add_state()

    def _setup_status_area(self):
        """状态栏固定高度，避免文字出现时把窗口撑大"""
        line_height = self.info_status.fontMetrics().lineSpacing()
        self.info_status.setWordWrap(True)
        self.info_status.setFixedHeight(line_height * 2 + 8)

    def _setup_key_table(self):
        table = self.keyTableWidget
        table.setColumnCount(4)
        table.setSelectionMode(NoSelection)
        table.setEditTriggers(NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(1, HeaderStretch)
        table.setColumnWidth(0, 26)
        table.setColumnWidth(2, 30)
        table.setColumnWidth(3, 30)
        table.verticalHeader().setDefaultSectionSize(28)
        # Key 是等宽字符，用 Consolas 等宽字体显示更整齐
        key_font = QFont("Consolas")
        key_font.setStyleHint(MonospaceStyleHint)
        key_font.setFixedPitch(True)
        point_size = self.font().pointSize()
        if point_size > 0:
            key_font.setPointSize(point_size)
        table.setFont(key_font)
        self.mLineEdit_key.setFont(key_font)

    def _init_subdomain(self):
        self.subdomainComboBox.addItems(list(SUBDOMAINS))
        index = self.subdomainComboBox.findText(self.conf.subdomain)
        self.subdomainComboBox.setCurrentIndex(max(index, 0))

    def _init_toggles(self):
        self.checkBox_key_rand.setChecked(self.conf.random_key)
        self.checkBox_domain_rand.setChecked(self.conf.random_subdomain)
        self._apply_subdomain_random_state()

    def _connect_signals(self):
        self.mLineEdit_key.textChanged.connect(self._on_key_text_changed)
        self.mLineEdit_key.returnPressed.connect(self._on_add_key)
        self.saveButton.clicked.connect(self._on_add_key)
        self.keyTableWidget.currentCellChanged.connect(self._on_current_cell_changed)
        self.checkBox_key_rand.stateChanged.connect(self._on_key_random_toggled)
        self.subdomainComboBox.currentTextChanged.connect(self._on_subdomain_changed)
        self.checkBox_domain_rand.stateChanged.connect(
            self._on_subdomain_random_toggled
        )
        self.pushButton_map_manager.clicked.connect(self._open_map_manager)
        self.pushButton_close.clicked.connect(self.reject)
        self.verifier.started.connect(self._on_verify_started)
        self.verifier.verified.connect(self._on_key_verified)
        self.verifier.failed.connect(self._on_key_failed)
        self.verifier.finished.connect(self._update_add_state)

    def _refresh_key_list(self):
        """根据配置重建 Key 列表，选中项即当前使用的 Key"""
        keys = self.conf.key_list
        active = self.conf.active_key
        if active not in keys:
            active = keys[0] if keys else ""
            self.conf.active_key = active

        self._loading = True
        try:
            table = self.keyTableWidget
            table.clearContents()
            table.setRowCount(0)
            if not keys:
                self.label_key_list_hint.setText(
                    "尚未添加 Key，请在下方输入后点击「验证并添加」"
                )
            table.setRowCount(len(keys))
            for row, key in enumerate(keys):
                check_item = QTableWidgetItem()
                check_item.setTextAlignment(AlignCenter)
                table.setItem(row, 0, check_item)
                item = QTableWidgetItem(mask_key(key))
                item.setData(UserRole, key)
                table.setItem(row, 1, item)
                table.setCellWidget(
                    row,
                    2,
                    self._make_row_button(
                        "mActionEditCopy.svg",
                        "复制",
                        lambda _=False, k=key: self._on_copy_key(k),
                    ),
                )
                table.setCellWidget(
                    row,
                    3,
                    self._make_row_button(
                        "mActionDeleteSelected.svg",
                        "删除",
                        lambda _=False, k=key: self._on_delete_key(k),
                    ),
                )
            self._update_current_marker()
        finally:
            self._loading = False

    def _make_row_button(self, icon_name: str, tooltip: str, slot) -> QtWidgets.QWidget:
        """生成居中的行内图标按钮容器"""
        container = QtWidgets.QWidget(self.keyTableWidget)
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        button = QToolButton(container)
        button.setAutoRaise(True)
        button.setIcon(QgsApplication.getThemeIcon(icon_name))
        button.setIconSize(QSize(16, 16))
        button.setFixedSize(24, 24)
        button.setToolTip(tooltip)
        button.clicked.connect(slot)
        layout.addWidget(button, 0, AlignCenter)
        return container

    def _update_current_marker(self):
        """用对钩标记当前 Key；随机模式下不显示当前 Key"""
        active = self.conf.active_key
        random_on = self.conf.random_key
        check_icon = icons["check"]
        if self.keyTableWidget.rowCount() > 0:
            self.label_key_list_hint.setText(
                "已保存的 Key（随机模式，不区分当前 Key）"
                if random_on
                else "已保存的 Key（对钩标记当前使用的 Key）"
            )
        for row in range(self.keyTableWidget.rowCount()):
            check_item = self.keyTableWidget.item(row, 0)
            key_item = self.keyTableWidget.item(row, 1)
            if check_item is None or key_item is None:
                continue
            key = key_item.data(UserRole) or ""
            is_current = bool(active) and key == active and not random_on
            check_item.setIcon(check_icon if is_current else QIcon())
            if is_current:
                key_item.setToolTip("当前使用的 Key")
            elif random_on:
                key_item.setToolTip("随机模式下不区分当前 Key")
            else:
                key_item.setToolTip("点击设为当前 Key")

    def _update_add_state(self):
        text = self.mLineEdit_key.text()
        result = check_key_format(text)
        self.label_key_length.setText(f"{len(text)}/{KEY_LENGTH}")
        if not text:
            self.label_key_length.setStyleSheet(f"color: {STATUS_COLORS['info']};")
        elif result.is_valid:
            self.label_key_length.setStyleSheet("")
        else:
            self.label_key_length.setStyleSheet(f"color: {STATUS_COLORS['error']};")

        busy = self.verifier.is_busy
        self.mLineEdit_key.setEnabled(not busy)
        self.saveButton.setEnabled(result.is_valid and not busy)
        self.saveButton.setText("验证中…" if busy else "验证并添加")

    def _on_key_text_changed(self):
        text = self.mLineEdit_key.text()
        filtered = "".join(c for c in text if c.isprintable() and not c.isspace())
        if filtered != text:
            self.mLineEdit_key.setText(filtered)
            return
        self._update_add_state()

    def _on_add_key(self):
        if self.verifier.is_busy:
            return
        key = self.mLineEdit_key.text()
        result = check_key_format(key)
        if not result.is_valid:
            self.show_status(result.message, "error")
            return
        if key in self.conf.key_list:
            self.mLineEdit_key.clear()
            self.conf.active_key = key
            self._refresh_key_list()
            self.show_status("该 Key 已存在，已设为当前 Key", "info")
            return
        self.verifier.verify(key)

    def _on_verify_started(self):
        self.show_status("正在验证 Key…", "info")
        self._update_add_state()

    def _on_key_verified(self, key: str):
        keys = self.conf.key_list
        if key not in keys:
            keys.append(key)
            self.conf.key_list = keys
        self.conf.active_key = key
        self.mLineEdit_key.clear()
        self._refresh_key_list()
        self._clear_status()

    def _on_key_failed(self, message: str):
        self.show_status(message, "error")

    def _on_current_cell_changed(
        self, current_row, _current_column, _previous_row, _previous_column
    ):
        if self._loading or current_row < 0:
            return
        if not self.conf.random_key:
            item = self.keyTableWidget.item(current_row, 1)
            key = (item.data(UserRole) or "") if item else ""
            if key and key != self.conf.active_key:
                self.conf.active_key = key
                self._update_current_marker()
        self._clear_current_cell()

    def _clear_current_cell(self):
        """清除 current index，避免选中行的背景色残留"""
        self._loading = True
        try:
            self.keyTableWidget.setCurrentCell(-1, -1)
        finally:
            self._loading = False

    def _on_copy_key(self, key: str):
        if not key:
            return
        QApplication.clipboard().setText(key, ModeClipboard)
        self.show_status(f"已复制 {mask_key(key)} 到剪贴板", "success")

    def _on_delete_key(self, key: str):
        if not key:
            return
        answer = QMessageBox.question(
            self, "删除 Key", f"确定要删除 {mask_key(key)} 吗？"
        )
        if answer != ButtonYes:
            return
        keys = [item for item in self.conf.key_list if item != key]
        self.conf.key_list = keys
        if self.conf.active_key == key:
            self.conf.active_key = keys[0] if keys else ""
        self._refresh_key_list()

    def _on_key_random_toggled(self, *_args):
        enabled = self.checkBox_key_rand.isChecked()
        self.conf.random_key = enabled
        self._update_current_marker()

    def _on_subdomain_changed(self, value: str):
        if self._loading:
            return
        self.conf.subdomain = value

    def _apply_subdomain_random_state(self):
        self.subdomainComboBox.setEnabled(not self.checkBox_domain_rand.isChecked())

    def _on_subdomain_random_toggled(self, *_args):
        enabled = self.checkBox_domain_rand.isChecked()
        self.conf.random_subdomain = enabled
        self._apply_subdomain_random_state()

    def _open_map_manager(self):
        dialog = MapManagerDialog(self)
        try:
            accepted = exec_dialog(dialog)
        finally:
            dialog.deleteLater()
        if accepted:
            self.maps_changed.emit()

    def show_status(self, message: str, level: str = "info"):
        """显示状态信息，错误信息保留到下次操作"""
        self._status_timer.stop()
        self.info_status.setStyleSheet(f"color: {STATUS_COLORS[level]};")
        self.info_status.setText(message)
        self.info_status.setToolTip(message if level == "error" else "")
        if level != "error":
            self._status_timer.start(STATUS_TIMEOUT_MS)

    def _clear_status(self):
        self._status_timer.stop()
        self.info_status.clear()
        self.info_status.setToolTip("")

    def reject(self):
        self.verifier.abort()
        super().reject()
