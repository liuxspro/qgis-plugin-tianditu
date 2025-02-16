# Form implementation generated from reading ui file './tianditu_tools/ui/sd.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from qgis.PyQt import QtCore, QtGui, QtWidgets


class Ui_SdDockWidget(object):
    def setupUi(self, SdDockWidget):
        SdDockWidget.setObjectName("SdDockWidget")
        SdDockWidget.resize(376, 442)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        SdDockWidget.setFont(font)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(parent=self.dockWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mLineEdit_sdtk = QgsPasswordLineEdit(parent=self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(8)
        self.mLineEdit_sdtk.setFont(font)
        self.mLineEdit_sdtk.setObjectName("mLineEdit_sdtk")
        self.horizontalLayout.addWidget(self.mLineEdit_sdtk)
        self.pushButton_save = QtWidgets.QPushButton(parent=self.groupBox)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(8)
        self.pushButton_save.setFont(font)
        self.pushButton_save.setObjectName("pushButton_save")
        self.horizontalLayout.addWidget(self.pushButton_save)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.listWidget = QtWidgets.QListWidget(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMaximumSize(QtCore.QSize(16777215, 58))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.listWidget.setFont(font)
        self.listWidget.setAutoScroll(True)
        self.listWidget.setAutoScrollMargin(80)
        self.listWidget.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_4.addWidget(self.listWidget)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self.dockWidgetContents)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBox = QtWidgets.QCheckBox(parent=self.groupBox_3)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.pushButton_search = QtWidgets.QPushButton(parent=self.groupBox_3)
        self.pushButton_search.setObjectName("pushButton_search")
        self.horizontalLayout_2.addWidget(self.pushButton_search)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.treeWidget = QtWidgets.QTreeWidget(parent=self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.treeWidget.setFont(font)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.treeWidget.headerItem().setTextAlignment(1, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.treeWidget.headerItem().setTextAlignment(2, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.treeWidget.headerItem().setTextAlignment(3, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.treeWidget.headerItem().setTextAlignment(4, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout_2.addWidget(self.treeWidget)
        self.verticalLayout.addWidget(self.groupBox_3)
        SdDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(SdDockWidget)
        QtCore.QMetaObject.connectSlotsByName(SdDockWidget)

    def retranslateUi(self, SdDockWidget):
        _translate = QtCore.QCoreApplication.translate
        SdDockWidget.setWindowTitle(_translate("SdDockWidget", "天地图·山东"))
        self.groupBox.setTitle(_translate("SdDockWidget", "Token 设置"))
        self.pushButton_save.setText(_translate("SdDockWidget", "保存"))
        self.label.setText(_translate("SdDockWidget", "<html><head/><body><p><a href=\"https://mp.weixin.qq.com/s/CcdjjjsBk7rNlxalBjUXIg\"><span style=\" text-decoration: underline; color:#0000ff;\">Token 申请方法及使用说明</span></a></p></body></html>"))
        self.groupBox_2.setTitle(_translate("SdDockWidget", "服务资源"))
        self.groupBox_3.setTitle(_translate("SdDockWidget", "历史影像"))
        self.checkBox.setText(_translate("SdDockWidget", "根据当前画布范围"))
        self.pushButton_search.setText(_translate("SdDockWidget", "查询历史影像"))
        self.treeWidget.headerItem().setText(0, _translate("SdDockWidget", "名称"))
        self.treeWidget.headerItem().setText(1, _translate("SdDockWidget", "时间"))
        self.treeWidget.headerItem().setText(2, _translate("SdDockWidget", "分辨率（m）"))
        self.treeWidget.headerItem().setText(3, _translate("SdDockWidget", "URL"))
        self.treeWidget.headerItem().setText(4, _translate("SdDockWidget", "el"))
from qgspasswordlineedit import QgsPasswordLineEdit
