from qgis.core import QgsProject, QgsRasterLayer, QgsMessageLog, Qgis


def push_message(iface, title: str, message: str):
    """
    将具有默认超时时间的信息推送到消息栏。
    https://qgis.org/pyqgis/3.44/gui/QgsMessageBar.html#qgis.gui.QgsMessageBar.pushInfo
    Args:
    iface : iface
    title (str): 消息标题
    message (str): 消息
    """
    iface.messageBar().pushInfo(
        title,
        message,
    )


def add_raster_layer(
    uri: str, name: str, provider_type: str = "wms"
) -> QgsRasterLayer | None:
    """QGIS 添加栅格图层

    Args:
        uri (str): 栅格图层 uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)
    Reference: https://qgis.org/pyqgis/3.32/core/QgsRasterLayer.html
    """
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
        return raster_layer
    log_message(f"无效的图层 Invalid Layer: \n{uri}")
    return None


def log_message(message: str):
    QgsMessageLog.logMessage(message, "Tianditu-Tools", Qgis.Info)
