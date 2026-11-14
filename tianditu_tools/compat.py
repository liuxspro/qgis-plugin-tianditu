from qgis.PyQt.QtCore import QT_VERSION_STR, Qt
from qgis.PyQt.QtGui import QClipboard, QFont, QPainter
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QToolButton,
)

QT_MAJOR_VERSION = int(QT_VERSION_STR.split(".")[0])
IS_QT5 = QT_MAJOR_VERSION == 5
IS_QT6 = QT_MAJOR_VERSION == 6

if IS_QT5:
    # Qt 5 版本
    from .ui.sd_5 import Ui_SdDockWidget  # noqa  # pylint: disable=unused-import
    from .ui.sd_timeline_5 import (  # noqa  # pylint: disable=unused-import
        Ui_SdTimelineDock,  # noqa  # pylint: disable=unused-import
    )
    from .ui.sd_token_5 import Ui_SdTokenDialog  # noqa  # pylint: disable=unused-import
    from .ui.search_5 import Ui_SearchDockWidget  # noqa  # pylint: disable=unused-import
    from .ui.setting_5 import Ui_SettingDialog  # noqa  # pylint: disable=unused-import
    from .ui.mapmanager_5 import (  # noqa  # pylint: disable=unused-import
        Ui_MapManagerDialog,  # noqa  # pylint: disable=unused-import
    )  # noqa  # pylint: disable=unused-import

    # 枚举值改变
    LeftDockWidgetArea = Qt.LeftDockWidgetArea
    RightDockWidgetArea = Qt.RightDockWidgetArea
    BottomDockWidgetArea = Qt.BottomDockWidgetArea
    AlignCenter = Qt.AlignCenter
    DescendingOrder = Qt.DescendingOrder
    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
    PartiallyChecked = Qt.PartiallyChecked
    MatchExactly = Qt.MatchExactly
    MenuButtonPopup = QToolButton.MenuButtonPopup
    NoError = QNetworkReply.NoError
    HttpStatusCodeAttribute = QNetworkRequest.HttpStatusCodeAttribute
    ModeClipboard = QClipboard.Clipboard
    ButtonYes = QMessageBox.Yes
    UserRole = Qt.UserRole
    PlainText = Qt.PlainText
    MonospaceStyleHint = QFont.Monospace
    NoSelection = QAbstractItemView.NoSelection
    SingleSelection = QAbstractItemView.SingleSelection
    NoEditTriggers = QAbstractItemView.NoEditTriggers
    HeaderStretch = QHeaderView.Stretch
    # 自绘控件相关
    LeftButton = Qt.LeftButton
    StrongFocus = Qt.StrongFocus
    KeyHome = Qt.Key_Home
    KeyEnd = Qt.Key_End
    KeyLeft = Qt.Key_Left
    KeyRight = Qt.Key_Right
    AlignLeft = Qt.AlignLeft
    AlignRight = Qt.AlignRight
    AlignVCenter = Qt.AlignVCenter
    NoPen = Qt.NoPen
    Antialiasing = QPainter.Antialiasing

if IS_QT6:
    # QT6 版本

    from .ui.sd import Ui_SdDockWidget  # noqa  # pylint: disable=unused-import
    from .ui.sd_timeline import (  # noqa  # pylint: disable=unused-import
        Ui_SdTimelineDock,  # noqa  # pylint: disable=unused-import
    )
    from .ui.sd_token import Ui_SdTokenDialog  # noqa  # pylint: disable=unused-import
    from .ui.setting import Ui_SettingDialog  # noqa  # pylint: disable=unused-import
    from .ui.search import (  # noqa # pylint: disable=unused-import
        Ui_SearchDockWidget,  # noqa # pylint: disable=unused-import
    )  # noqa  # pylint: disable=unused-import
    from .ui.mapmanager import (  # noqa  # pylint: disable=unused-import
        Ui_MapManagerDialog,  # noqa  # pylint: disable=unused-import
    )  # noqa  # pylint: disable=unused-import

    # 枚举值改变
    LeftDockWidgetArea = Qt.DockWidgetArea.LeftDockWidgetArea
    RightDockWidgetArea = Qt.DockWidgetArea.RightDockWidgetArea
    BottomDockWidgetArea = Qt.DockWidgetArea.BottomDockWidgetArea
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    DescendingOrder = Qt.SortOrder.DescendingOrder
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
    PartiallyChecked = Qt.CheckState.PartiallyChecked
    MatchExactly = Qt.MatchFlag.MatchExactly
    MenuButtonPopup = QToolButton.ToolButtonPopupMode.MenuButtonPopup
    NoError = QNetworkReply.NetworkError.NoError
    HttpStatusCodeAttribute = QNetworkRequest.Attribute.HttpStatusCodeAttribute
    ModeClipboard = QClipboard.Mode.Clipboard
    ButtonYes = QMessageBox.StandardButton.Yes
    UserRole = Qt.ItemDataRole.UserRole
    PlainText = Qt.TextFormat.PlainText
    MonospaceStyleHint = QFont.StyleHint.Monospace
    NoSelection = QAbstractItemView.SelectionMode.NoSelection
    SingleSelection = QAbstractItemView.SelectionMode.SingleSelection
    NoEditTriggers = QAbstractItemView.EditTrigger.NoEditTriggers
    HeaderStretch = QHeaderView.ResizeMode.Stretch
    # 自绘控件相关
    LeftButton = Qt.MouseButton.LeftButton
    StrongFocus = Qt.FocusPolicy.StrongFocus
    KeyHome = Qt.Key.Key_Home
    KeyEnd = Qt.Key.Key_End
    KeyLeft = Qt.Key.Key_Left
    KeyRight = Qt.Key.Key_Right
    AlignLeft = Qt.AlignmentFlag.AlignLeft
    AlignRight = Qt.AlignmentFlag.AlignRight
    AlignVCenter = Qt.AlignmentFlag.AlignVCenter
    NoPen = Qt.PenStyle.NoPen
    Antialiasing = QPainter.RenderHint.Antialiasing


def exec_dialog(dialog) -> int:
    """兼容 Qt5 / Qt6 的 modal 对话框执行"""
    if IS_QT5:
        return dialog.exec_()
    return dialog.exec()
