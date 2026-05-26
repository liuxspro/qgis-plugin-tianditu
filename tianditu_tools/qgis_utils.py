from qgis.core import (
    Qgis,
    QgsFeature,
    QgsGeometry,
    QgsMessageLog,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)


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


def push_warning(iface, title: str, message: str):
    iface.messageBar().pushWarning(
        title,
        message,
    )


def push_error(iface, title: str, message: str):
    iface.messageBar().pushCritical(
        title,
        message,
    )


def create_crs84_point_layer(name: str, point: QgsPointXY):
    layer = QgsVectorLayer("Point?crs=EPSG:4326&field=Name:string", name, "memory")
    pr = layer.dataProvider()
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPointXY(point))
    feature.setAttributes([name])
    pr.addFeature(feature)
    return layer, feature


def create_raster_layer(uri: str, name: str, provider_type: str = "wms"):
    """创建栅格图层但不添加到项目（用于图层组场景）

    Args:
        uri (str): 栅格图层 uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)

    Returns:
        QgsRasterLayer or None: 创建的图层，无效时返回 None
    """
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    if raster_layer.isValid():
        return raster_layer
    log_message(f"无效的图层 Invalid Layer: \n{uri}")
    return None


def add_raster_layer(uri: str, name: str, provider_type: str = "wms"):
    """QGIS 添加栅格图层

    Args:
        uri (str): 栅格图层 uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)
    Reference: https://qgis.org/pyqgis/3.32/core/QgsRasterLayer.html
    """
    raster_layer = create_raster_layer(uri, name, provider_type)
    if raster_layer:
        QgsProject.instance().addMapLayer(raster_layer)
        return raster_layer
    return None


def add_raster_layer_group(layers, group_name, provider_type="wms"):
    """添加一个包含多个栅格图层的图层组

    Args:
        layers: [(uri, name), ...] 图层列表
        group_name: 图层组名称
        provider_type: 栅格图层类型

    Returns:
        QgsLayerTreeGroup or None
    """
    root = QgsProject.instance().layerTreeRoot()
    group = root.insertGroup(0, group_name)
    for uri, name in layers:
        raster_layer = create_raster_layer(uri, name, provider_type)
        if raster_layer:
            QgsProject.instance().addMapLayer(raster_layer, False)
            group.addLayer(raster_layer)
    return group


def log_message(message: str):
    QgsMessageLog.logMessage(message, "Tianditu-Tools", Qgis.Info)
