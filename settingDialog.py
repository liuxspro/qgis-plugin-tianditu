from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from .configSetting import ConfigFile, CONFIG_FILE_PATH
from .ui.setting import Ui_SettingDialog
from .utils import tianditu_map_url, check_url_status

cfg = ConfigFile(CONFIG_FILE_PATH)


class CheckThread(QThread):
    check_finished = pyqtSignal(str)

    def run(self):
        url = tianditu_map_url('vec', self.key)
        tile_url = url.format(x=0, y=0, z=0)
        check_msg = check_url_status(tile_url)
        if check_msg['code'] == 0:
            self.check_finished.emit('正常')
            cfg.setValue('Tianditu', 'keyisvalid', 'True')
        else:
            error_msg = f"{check_msg['msg']}: {check_msg['resolve']}"
            self.check_finished.emit(error_msg)
            cfg.setValue('Tianditu', 'keyisvalid', 'False')


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    def __init__(self, extra_map_action, parent=None):
        super(SettingDialog, self).__init__(parent)
        self.check_thread = None
        self.extra_map_action = extra_map_action
        self.key = cfg.getValue('Tianditu', 'key')
        self.keyisvalid = cfg.getValueBoolean('Tianditu', 'keyisvalid')
        self.extramap_enabled = cfg.getValueBoolean('Other', 'extramap')
        self.setupUi(self)
        self.mLineEdit_key.setText(self.key)
        if self.keyisvalid:
            self.label_keystatus.setText('正常')
        else:
            self.label_keystatus.setText('无效')
        self.pushButton.clicked.connect(self.check)
        self.checkBox.setChecked(self.extramap_enabled)
        self.checkBox.stateChanged.connect(self.enable_extramap)

    def check(self):
        # save
        cfg.setValue('Tianditu', 'key', self.mLineEdit_key.text())
        self.label_keystatus.setText('检查中...')
        self.check_thread = CheckThread()
        self.check_thread.key = self.mLineEdit_key.text()
        self.check_thread.check_finished.connect(self.label_keystatus.setText)
        self.check_thread.start()

    def enable_extramap(self):
        if self.checkBox.isChecked():
            cfg.setValue('Other', 'extramap', 'True')
            self.extra_map_action.setEnabled(True)
        else:
            cfg.setValue('Other', 'extramap', 'False')
            self.extra_map_action.setEnabled(False)
