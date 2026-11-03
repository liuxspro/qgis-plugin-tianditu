from qgis.PyQt import QtWidgets

from ...compat import Ui_MapManagerDialog
from ...utils import PluginDir
from .tree import MapManager


class MapManagerDialog(QtWidgets.QDialog, Ui_MapManagerDialog):
    """独立的地图管理对话框，确定后保存启用的地图源"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.mapm = MapManager(PluginDir.joinpath("maps"), parent=self)
        self.horizontalLayout_tree.addWidget(self.mapm)

        self.filterEdit.textChanged.connect(self.mapm.apply_filter)
        self.pushButton_check_all.clicked.connect(
            lambda: self.mapm.set_all_checked(True)
        )
        self.pushButton_uncheck_all.clicked.connect(
            lambda: self.mapm.set_all_checked(False)
        )
        self.pushButton_load.clicked.connect(self.mapm.load_map_package_clicked)
        self.pushButton_ok.clicked.connect(self._on_ok)
        self.pushButton_cancel.clicked.connect(self.reject)
        self.mapm.counts_changed.connect(self._update_count)
        self._update_count(*self.mapm.counts())

    def _on_ok(self):
        self.mapm.save_state()
        self.accept()

    def _update_count(self, checked: int, total: int):
        self.label_count.setText(f"已启用 {checked} / {total} 项")
