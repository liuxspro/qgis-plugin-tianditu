# Form implementation generated from reading ui file './tianditu_tools/ui/search.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from qgis.PyQt import QtCore, QtGui, QtWidgets


class Ui_SearchDockWidget(object):
    def setupUi(self, SearchDockWidget):
        SearchDockWidget.setObjectName("SearchDockWidget")
        SearchDockWidget.resize(422, 303)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        SearchDockWidget.setFont(font)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.tab)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(parent=self.tab)
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.tab_2)
        self.lineEdit_2.setInputMask("")
        self.lineEdit_2.setText("")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.tab_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(parent=self.tab_2)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.label.setOpenExternalLinks(False)
        self.label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(parent=self.tab_2)
        self.label_2.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.label_2.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.tab_3)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_2.addWidget(self.lineEdit_3)
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.tab_3)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.label_3 = QtWidgets.QLabel(parent=self.tab_3)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(parent=self.tab_3)
        self.label_4.setText("")
        self.label_4.setWordWrap(True)
        self.label_4.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        SearchDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(SearchDockWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SearchDockWidget)

    def retranslateUi(self, SearchDockWidget):
        _translate = QtCore.QCoreApplication.translate
        SearchDockWidget.setWindowTitle(_translate("SearchDockWidget", "天地图API-搜索"))
        self.lineEdit.setPlaceholderText(_translate("SearchDockWidget", "请输入地名"))
        self.pushButton.setText(_translate("SearchDockWidget", "搜索"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("SearchDockWidget", "地名搜索"))
        self.lineEdit_2.setPlaceholderText(_translate("SearchDockWidget", "请输入地名"))
        self.pushButton_2.setText(_translate("SearchDockWidget", "查询"))
        self.label.setText(_translate("SearchDockWidget", "搜索结果："))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("SearchDockWidget", "地理编码查询"))
        self.lineEdit_3.setPlaceholderText(_translate("SearchDockWidget", "请输入经纬度：经度,纬度"))
        self.pushButton_3.setText(_translate("SearchDockWidget", "查询"))
        self.label_3.setText(_translate("SearchDockWidget", "搜索结果"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("SearchDockWidget", "逆地理编码查询"))
