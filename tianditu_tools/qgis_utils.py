from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsMessageLog,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QTimer


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


def create_crs84_point_layer(name: str, point: QgsPointXY, crs=None):
    """创建一个只包含单个点的内存图层

    Args:
        name: 图层名称
        point: 点的 WGS84 坐标
        crs: 图层坐标系，默认 EPSG:4326；传入其他坐标系时会先把点转换过去
    """
    wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    target_crs = crs if crs is not None and crs.isValid() else wgs84
    if target_crs != wgs84:
        transform = QgsCoordinateTransform(wgs84, target_crs, QgsProject.instance())
        point = transform.transform(point)
    layer = QgsVectorLayer(
        f"Point?crs={target_crs.authid()}&field=Name:string", name, "memory"
    )
    pr = layer.dataProvider()
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPointXY(point))
    feature.setAttributes([name])
    pr.addFeature(feature)
    return layer, feature


def search_result_crs(iface, project_is_empty: bool):
    """确定地名搜索结果点图层使用的坐标系，并同步工程/画布 CRS。

    空工程时 QGIS 会在事件循环下一轮把工程 CRS 改成“第一个图层的 CRS”
    （QgsLayerTreeMapCanvasBridge::setCanvasLayers，对应选项
    “工程坐标系使用第一个加入图层的坐标系”），并把画布范围重新投影。
    所以空工程时直接让点图层用 EPSG:3857：1:18056 对应约 5km 的视野，
    而且 QGIS 随后的 CRS 同步不会再把工程 CRS 改回 4326、把画布范围
    重投影成错误的比例尺。

    Args:
        iface: QgisInterface
        project_is_empty (bool): 添加图层前工程是否没有任何图层

    Returns:
        QgsCoordinateReferenceSystem: 点图层使用的坐标系（非空工程为 EPSG:4326）
    """
    wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    if not project_is_empty:
        return wgs84
    mercator = QgsCoordinateReferenceSystem("EPSG:3857")
    if QgsProject.instance().crs() != mercator:
        QgsProject.instance().setCrs(mercator)
    canvas = iface.mapCanvas()
    if canvas.mapSettings().destinationCrs() != mercator:
        canvas.setDestinationCrs(mercator)
    return mercator


def zoom_to_point(iface, point: QgsPointXY, scale: float = 18056.0):
    """延后一轮事件循环，把画布中心移到 point 并设置绝对比例尺 scale。

    不能用 zoomToFeatureIds + zoomScale 组合：对单个点要素，
    QgsMapCanvas::zoomToFeatureExtent 只是保持当前范围大小、把中心移到该点，
    而 zoomScale 是相对当前比例尺缩放。

    也不能同步缩放：空工程添加第一个图层后，QGIS 会在事件循环下一轮
    （QgsLayerTreeMapCanvasBridge::setCanvasLayers，QueuedConnection）把工程 CRS
    改成第一个图层的 CRS，并调用 zoomToProjectExtent()。单点图层的范围是零面积，
    会被 QgsMapLayerUtils::combinedExtent 按“坐标 * 1e-8”膨胀成类米级小矩形，
    于是自动缩放到 1:1 这种无意义比例，并覆盖掉我们的缩放。延后一轮才能覆盖它。

    Args:
        iface: QgisInterface
        point (QgsPointXY): WGS84 坐标点
        scale (float): 目标比例尺分母
    """
    QTimer.singleShot(0, lambda: _zoom_to_point(iface, point, scale))


def _zoom_to_point(iface, point: QgsPointXY, scale: float):
    canvas = iface.mapCanvas()
    canvas_crs = canvas.mapSettings().destinationCrs()
    if not canvas_crs.isValid():
        canvas_crs = QgsProject.instance().crs()
        if not canvas_crs.isValid():
            canvas_crs = QgsCoordinateReferenceSystem("EPSG:3857")
        canvas.setDestinationCrs(canvas_crs)

    transform = QgsCoordinateTransform(
        QgsCoordinateReferenceSystem("EPSG:4326"), canvas_crs, QgsProject.instance()
    )
    center = transform.transform(point)

    # 先设置一个以点为中心的有效范围，让 extent/scale 有确定值；
    # 空工程时 mapUnitsPerPixel() 为 0 或 NaN，用临时值占位即可，
    # 范围大小随后会被 zoomScale 覆盖。
    mupp = canvas.mapUnitsPerPixel()
    if not mupp > 0:
        mupp = 1.0
    size = canvas.mapSettings().outputSize()
    canvas.setExtent(
        QgsRectangle.fromCenterAndSize(
            center, mupp * size.width(), mupp * size.height()
        )
    )
    canvas.zoomScale(scale)


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
