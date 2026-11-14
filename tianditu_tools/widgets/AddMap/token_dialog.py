from qgis.PyQt import QtWidgets

from ...compat import Ui_SdTokenDialog
from ...utils import PluginConfig

STATUS_COLORS = {
    "info": "#808080",
    "error": "#cf222e",
}


class SdTokenDialog(QtWidgets.QDialog, Ui_SdTokenDialog):
    """天地图·山东 Token 设置"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.conf = PluginConfig()
        self.setupUi(self)
        self.pushButton_save.setDefault(True)
        self.pushButton_save.clicked.connect(self.save_token)
        self.pushButton_cancel.clicked.connect(self.reject)
        self.pushButton_clear.clicked.connect(self.clear_token)
        self.mLineEdit_token.returnPressed.connect(self.save_token)
        self._load_token()

    def _load_token(self):
        token = self.conf.get_value("Other/sd_tk") or ""
        self.mLineEdit_token.setText(token)
        if token:
            self.set_status("已保存 Token，重新输入可覆盖")

    def set_status(self, text: str, level: str = "info"):
        color = STATUS_COLORS.get(level, STATUS_COLORS["info"])
        self.label_status.setStyleSheet(f"color: {color};")
        self.label_status.setText(text)

    def save_token(self):
        token = self.mLineEdit_token.text().strip()
        if not token:
            self.set_status("Token 不能为空，如需删除请点击「清除 Token」", "error")
            return
        self.conf.set_value("Other/sd_tk", token)
        self.accept()

    def clear_token(self):
        if not (self.conf.get_value("Other/sd_tk") or ""):
            self.set_status("当前没有已保存的 Token")
            return
        self.conf.set_value("Other/sd_tk", "")
        self.accept()
