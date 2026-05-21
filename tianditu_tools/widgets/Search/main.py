from qgis.PyQt.QtWidgets import QAction

from ...compat import LeftDockWidgetArea
from ...qgis_utils import push_error
from ...utils import PluginConfig
from ..icons import icons
from .searchDock import SearchDockWidget

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
        # 断开 Action 自身的信号
        try:
            self.triggered.disconnect(self.openSearch)
        except (TypeError, RuntimeError):
            pass
        try:
            self.searchdockwidget.visibilityChanged.disconnect(
                self.onDockVisibilityChanged
            )
        except (TypeError, RuntimeError):
            pass
        # 清理 DockWidget 内部的资源
        self.searchdockwidget.cleanup()
        # 先关闭 DockWidget，使其从主窗口的 DockWidget 区域立即脱离
        self.searchdockwidget.close()
        # 立即解除父子关系，Plugin Reloader 在 unload 后即时扫描时就不会找到它
        self.searchdockwidget.setParent(None)
        # 从 QGIS 界面移除 DockWidget
        self.iface.removeDockWidget(self.searchdockwidget)
        # 将 Python 引用置空，帮助垃圾回收
        dockwidget = self.searchdockwidget
        self.searchdockwidget = None
        # 安全销毁
        dockwidget.deleteLater()
