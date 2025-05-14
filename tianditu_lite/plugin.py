from qgis.core import QgsApplication

from .provider import TiandituProvider


class TianDiTuLite:
    def __init__(self, iface):
        self.iface = iface
        self.tianditu_provider = TiandituProvider(self.iface)

    def initGui(self):
        self.registProvider()

    def registProvider(self):
        QgsApplication.instance().dataItemProviderRegistry().addProvider(
            self.tianditu_provider
        )

    def removeProvider(self):
        QgsApplication.instance().dataItemProviderRegistry().removeProvider(
            self.tianditu_provider
        )

    def unload(self):
        """Unload from the QGIS interface"""
        self.removeProvider()
