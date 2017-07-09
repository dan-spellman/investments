# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'showAllocations.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(441, 692)
        self.tableView = QtGui.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(10, 110, 411, 521))
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.addButton = QtGui.QPushButton(Dialog)
        self.addButton.setGeometry(QtCore.QRect(10, 80, 75, 23))
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 640, 320, 41))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.refreshPushButton = QtGui.QPushButton(self.layoutWidget)
        self.refreshPushButton.setObjectName(_fromUtf8("refreshPushButton"))
        self.gridLayout.addWidget(self.refreshPushButton, 0, 0, 1, 1)
        self.updateButton = QtGui.QPushButton(self.layoutWidget)
        self.updateButton.setObjectName(_fromUtf8("updateButton"))
        self.gridLayout.addWidget(self.updateButton, 0, 1, 1, 1)
        self.cancelButton = QtGui.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.gridLayout.addWidget(self.cancelButton, 0, 2, 1, 1)
        self.deleteButton = QtGui.QPushButton(self.layoutWidget)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.gridLayout.addWidget(self.deleteButton, 0, 3, 1, 1)
        self.layoutWidget1 = QtGui.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 10, 411, 68))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.gridLayout_2 = QtGui.QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_5 = QtGui.QLabel(self.layoutWidget1)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.layoutWidget1)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 0, 1, 1, 1)
        self.label_9 = QtGui.QLabel(self.layoutWidget1)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 0, 2, 1, 1)
        self.stockIdLineEdit = QtGui.QLineEdit(self.layoutWidget1)
        self.stockIdLineEdit.setObjectName(_fromUtf8("stockIdLineEdit"))
        self.gridLayout_2.addWidget(self.stockIdLineEdit, 1, 0, 1, 1)
        self.typeComboBox = QtGui.QComboBox(self.layoutWidget1)
        self.typeComboBox.setObjectName(_fromUtf8("typeComboBox"))
        self.gridLayout_2.addWidget(self.typeComboBox, 1, 1, 1, 1)
        self.allocationLineEdit = QtGui.QLineEdit(self.layoutWidget1)
        self.allocationLineEdit.setObjectName(_fromUtf8("allocationLineEdit"))
        self.gridLayout_2.addWidget(self.allocationLineEdit, 1, 2, 1, 1)
        self.layoutWidget.raise_()
        self.layoutWidget.raise_()
        self.tableView.raise_()
        self.addButton.raise_()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.addButton.setText(_translate("Dialog", "Add", None))
        self.refreshPushButton.setText(_translate("Dialog", "Refresh", None))
        self.updateButton.setText(_translate("Dialog", "Update", None))
        self.cancelButton.setText(_translate("Dialog", "Cancel", None))
        self.deleteButton.setText(_translate("Dialog", "Delete", None))
        self.label_5.setText(_translate("Dialog", "stock_id", None))
        self.label_8.setText(_translate("Dialog", "type", None))
        self.label_9.setText(_translate("Dialog", "allocation", None))

