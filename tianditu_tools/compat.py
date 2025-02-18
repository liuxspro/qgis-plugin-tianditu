from qgis.PyQt.QtCore import Qt, QT_VERSION_STR
from qgis.PyQt.QtGui import QClipboard
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QToolButton

QT_MAJOR_VERSION = int(QT_VERSION_STR.split(".")[0])
IS_QT5 = QT_MAJOR_VERSION == 5
IS_QT6 = QT_MAJOR_VERSION == 6

if IS_QT5:
    # Qt 5 版本
    from .ui.sd import Ui_SdDockWidget  # noqa  # pylint: disable=unused-import
    from .ui.search import Ui_SearchDockWidget  # noqa  # pylint: disable=unused-import
    from .ui.setting import Ui_SettingDialog  # noqa  # pylint: disable=unused-import

    # 枚举值改变
    LeftDockWidgetArea = Qt.LeftDockWidgetArea
    RightDockWidgetArea = Qt.RightDockWidgetArea
    AlignCenter = Qt.AlignCenter
    DescendingOrder = Qt.DescendingOrder
    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
    MatchExactly = Qt.MatchExactly
    MenuButtonPopup = QToolButton.MenuButtonPopup
    NoError = QNetworkReply.NoError
    HttpStatusCodeAttribute = QNetworkRequest.HttpStatusCodeAttribute
    ModeClipboard = QClipboard.Clipboard

if IS_QT6:
    # QT6 版本

    from .ui.sd_6 import Ui_SdDockWidget  # noqa  # pylint: disable=unused-import
    from .ui.setting_6 import Ui_SettingDialog  # noqa  # pylint: disable=unused-import
    from .ui.search_6 import (  # noqa # pylint: disable=unused-import
        Ui_SearchDockWidget,  # noqa # pylint: disable=unused-import
    )  # noqa  # pylint: disable=unused-import

    # 枚举值改变
    LeftDockWidgetArea = Qt.DockWidgetArea.LeftDockWidgetArea
    RightDockWidgetArea = Qt.DockWidgetArea.RightDockWidgetArea
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    DescendingOrder = Qt.SortOrder.DescendingOrder
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
    MatchExactly = Qt.MatchFlag.MatchExactly
    MenuButtonPopup = QToolButton.ToolButtonPopupMode.MenuButtonPopup
    NoError = QNetworkReply.NetworkError.NoError
    HttpStatusCodeAttribute = QNetworkRequest.Attribute.HttpStatusCodeAttribute
    ModeClipboard = QClipboard.Mode.Clipboard
