from .widgets.toolbar import TiandituToolbar


class TianDiTu:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar = TiandituToolbar(self.iface)

    def initGui(self):
        self.iface.addToolBar(self.toolbar)

    def unload(self):
        """Unload from the QGIS interface"""
        self.toolbar.remove_dock()
        mw = self.iface.mainWindow()
        mw.removeToolBar(self.toolbar)
        self.toolbar.deleteLater()
