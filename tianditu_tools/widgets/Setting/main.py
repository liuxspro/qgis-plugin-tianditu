from qgis.PyQt.QtWidgets import QAction

from .dialog import SettingDialog
from ..icons import icons
from ...compat import IS_QT5, IS_QT6


class SettingAction(QAction):
    def __init__(
        self,
        toolbar,
        parent=None,
    ):
        super().__init__(parent)
        self.setIcon(icons["setting"])
        self.setText("设置")
        self.triggered.connect(self.show_setting_dialog)
        self.toolbar = toolbar

    def show_setting_dialog(self):
        dlg = SettingDialog(toolbar=self.toolbar)
        if IS_QT5:
            dlg.exec_()
        if IS_QT6:
            dlg.exec()
