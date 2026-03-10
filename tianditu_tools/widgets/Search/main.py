from qgis.PyQt.QtWidgets import QAction

from .searchDock import SearchDockWidget
from ..icons import icons
from ...compat import LeftDockWidgetArea
from ...qgis_utils import push_error
from ...utils import PluginConfig

conf = PluginConfig()


class SearchAction(QAction):
    def __init__(
        self,
        iface,
        parent=None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.iface = iface
        self.setIcon(icons["search"])
        self.setText("搜索")
        self.searchdockwidget = SearchDockWidget(self.iface)
        self.searchdockwidget.visibilityChanged.connect(self.onDockVisibilityChanged)
        self.iface.addDockWidget(LeftDockWidgetArea, self.searchdockwidget)
        self.searchdockwidget.hide()
        self.setCheckable(True)
        self.triggered.connect(self.openSearch)

    def openSearch(self):
        key = conf.get_key()
        if key == "":
            self.setChecked(False)
            push_error(self.iface, "错误", "天地图 Key 未设置或 Key 无效")
            return

        if self.searchdockwidget.isHidden():
            self.searchdockwidget.show()
        else:
            self.searchdockwidget.hide()

    def onDockVisibilityChanged(self, is_visible):
        if not is_visible:
            self.setChecked(False)
        else:
            self.setChecked(True)

    def unload(self):
        self.iface.removeDockWidget(self.searchdockwidget)
