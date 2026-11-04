from qgis.PyQt.QtWidgets import QAction

from ...compat import exec_dialog
from ..icons import icons
from .dialog import SettingDialog


class SettingAction(QAction):
    def __init__(
        self,
        toolbar,
        parent=None,
    ):
        super().__init__(parent if parent is not None else toolbar)
        self.setIcon(icons["setting"])
        self.setText("设置")
        self.triggered.connect(self.show_setting_dialog)
        self.toolbar = toolbar

    def show_setting_dialog(self):
        dialog = SettingDialog(parent=self.toolbar.window())
        dialog.maps_changed.connect(self.toolbar.refresh_add_map_menu)
        try:
            exec_dialog(dialog)
        finally:
            dialog.deleteLater()
