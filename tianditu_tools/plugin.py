from .locator import TDTAdministrativeFilter, TDTGeocoderFilter
from .widgets.toolbar import TiandituToolbar


class TianDiTu:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar = TiandituToolbar(self.iface)
        self.locator_filter = None
        self.locator_adm_filter = None

    def initGui(self):
        self.iface.addToolBar(self.toolbar)

        # 注册 Locator Filters
        self.locator_filter = TDTGeocoderFilter(self.iface)
        self.iface.registerLocatorFilter(self.locator_filter)

        self.locator_adm_filter = TDTAdministrativeFilter(self.iface)
        self.iface.registerLocatorFilter(self.locator_adm_filter)

    def unload(self):
        """Unload from the QGIS interface"""
        # 注销 Locator Filters
        if self.locator_filter:
            self.iface.deregisterLocatorFilter(self.locator_filter)
            self.locator_filter = None

        if self.locator_adm_filter:
            self.iface.deregisterLocatorFilter(self.locator_adm_filter)
            self.locator_adm_filter = None

        self.toolbar.remove_dock()
        mw = self.iface.mainWindow()
        mw.removeToolBar(self.toolbar)
        self.toolbar.deleteLater()
