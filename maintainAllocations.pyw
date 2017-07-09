import sys
from showAllocations import *
from PyQt4 import QtSql, QtGui, QtCore

def createConnection():
    db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
    db.setHostName('localhost')
    db.setDatabaseName('investments')
    db.setUserName('root')
    db.setPassword('B1x2s3tr')
    db.open()
    print (db.lastError().text())
    return True

class MyForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable("allocations")
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model.setSort(0,0)
        self.model.select()
        self.allocationQuery = QtSql.QSqlQuery()
        self.getTypes()
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.sortByColumn(3,1)
        QtCore.QObject.connect(self.ui.updateButton, QtCore.SIGNAL('clicked()'),self.updateRecords)
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL('clicked()'),self.cancelChanges)
        QtCore.QObject.connect(self.ui.addButton, QtCore.SIGNAL('clicked()'),self.insertRecords)
        QtCore.QObject.connect(self.ui.deleteButton, QtCore.SIGNAL('clicked()'),self.deleteRecords)

    def getTypes(self):
        print ("Getting Allocation Types")
        self.filterStrList = [""]
        self.allocationQuery.exec_("SELECT DISTINCT type FROM allocations")
        while self.allocationQuery.next():
            type_id=self.allocationQuery.value(0).toString()
            self.ui.typeComboBox.addItem(type_id)

    def updateRecords(self):
        self.model.submitAll()
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.sortByColumn(3,1)
            
    def cancelChanges(self):
        self.model.revertAll()

    def insertRecords(self):
        print ("Inserting Records")
        insertStr = "INSERT INTO allocations (stock_id, type, allocation) VALUES("
        stock_id = self.ui.stockIdLineEdit.text()
        type = self.ui.typeComboBox.currentText()
        allocation = self.ui.allocationLineEdit.text()
        insertStr = insertStr + "'" + stock_id + "', " 
        insertStr = insertStr + "'" + type + "', " 
        insertStr = insertStr + allocation + ");"
        print (insertStr)
        self.allocationQuery.exec_(insertStr)
        self.model.select()
        self.ui.tableView.sortByColumn(3,1)
#        self.model.insertRow(0)
        
    def deleteRecords(self):
        self.model.removeRow(self.ui.tableView.currentIndex().row())

    def filterRecords(self):
        print (self.filterStrList[self.ui.accountComboBox.currentIndex()])
        self.model.setFilter(self.filterStrList[self.ui.accountComboBox.currentIndex()])

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if not createConnection():
        sys.exit(1)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())

        
