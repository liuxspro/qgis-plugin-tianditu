from qgis.PyQt.QtCore import QT_VERSION_STR
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtNetwork import QNetworkReply
from qgis.PyQt.QtWidgets import QToolButton

QT_MAJOR_VERSION = int(QT_VERSION_STR.split(".")[0])
IS_QT5 = QT_MAJOR_VERSION == 5
IS_QT6 = QT_MAJOR_VERSION == 6

if IS_QT5:
    # Qt 5 版本
    from .ui.sd import Ui_SdDockWidget
    from .ui.search import Ui_SearchDockWidget
    from .ui.setting import Ui_SettingDialog

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
if IS_QT6:
    # QT6 版本

    from .ui.sd_6 import Ui_SdDockWidget
    from .ui.search_6 import Ui_SearchDockWidget
    from .ui.setting_6 import Ui_SettingDialog

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


_UI = [Ui_SdDockWidget, Ui_SearchDockWidget, Ui_SettingDialog]
