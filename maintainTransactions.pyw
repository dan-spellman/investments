import sys
from showTransactions import *
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
        self.model.setTable("transactions")
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model.setSort(0,0)
        self.model.select()
        self.purchaseQuery = QtSql.QSqlQuery()
        self.getAccounts()
        self.getStocks()
        self.getTransactions()
        self.getRealized()
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.sortByColumn(1,1)
        QtCore.QObject.connect(self.ui.updateButton, QtCore.SIGNAL('clicked()'),self.updateRecords)
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL('clicked()'),self.cancelChanges)
        QtCore.QObject.connect(self.ui.addButton, QtCore.SIGNAL('clicked()'),self.insertRecords)
        QtCore.QObject.connect(self.ui.deleteButton, QtCore.SIGNAL('clicked()'),self.deleteRecords)
        QtCore.QObject.connect(self.ui.filterButton, QtCore.SIGNAL('clicked()'),self.filterRecords)

    def getAccounts(self):
        print ("Getting Accounts")
        self.ui.accountComboBox.addItem("ALL")
        self.accountFilterStrList = [""]
        self.accountNameStrList = []
        self.purchaseQuery.exec_("SELECT DISTINCT account_id, account_name FROM transactions")
        while self.purchaseQuery.next():
            account_id=self.purchaseQuery.value(0).toString()
            account_name=self.purchaseQuery.value(1).toString()
            self.ui.accountComboBox.addItem(account_id)
            self.ui.accountIdComboBox.addItem(account_id)
            filterStr = ("account_id = '%s'" %account_id)
            self.accountFilterStrList.append(filterStr)
            self.accountNameStrList.append(account_name)

    def getStocks(self):
        print ("Getting Stocks")
        self.ui.stockComboBox.addItem("ALL")
        self.stockFilterStrList = [""]
        self.purchaseQuery.exec_("SELECT DISTINCT stock_id FROM transactions ORDER BY stock_id ASC")
        while self.purchaseQuery.next():
            stock_id=self.purchaseQuery.value(0).toString()
            self.ui.stockComboBox.addItem(stock_id)
            filterStr = ("stock_id = '%s'" %stock_id)
            self.stockFilterStrList.append(filterStr)

    def getRealized(self):
        self.ui.realizedComboBox.addItem("UNREALIZED")
        self.ui.realizedComboBox.addItem("REALIZED")

    def getTransactions(self):
        print ("Getting Transactions")
        self.purchaseQuery.exec_("SELECT DISTINCT trans_type FROM transactions")
        while self.purchaseQuery.next():
            trans_type=self.purchaseQuery.value(0).toString()
            self.ui.transTypeComboBox.addItem(trans_type)

    def updateRecords(self):
        self.model.submitAll()
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.sortByColumn(1,1)
            
    def cancelChanges(self):
        self.model.revertAll()

    def insertRecords(self):
        print ("Inserting Records")
        insertStr = "INSERT INTO transactions (trans_dt, trans_type, realized, trans_amount, quantity, stock_id, price, commission, account_id, account_name) VALUES("
        trans_dt = self.ui.dateEdit.date().toString(QtCore.Qt.ISODate)
        trans_type = self.ui.transTypeComboBox.currentText()
        realized = ("%s"%self.ui.realizedComboBox.currentIndex())
        trans_amount = self.ui.transAmountLineEdit.text()
        quantity = self.ui.quantityLineEdit.text()
        stock_id = self.ui.stockIdLineEdit.text()
        price = self.ui.priceLineEdit.text()
        commission = self.ui.commissionLineEdit.text()
        account_id = self.ui.accountIdComboBox.currentText()
        account_name = self.accountNameStrList[self.ui.accountIdComboBox.currentIndex()]
        insertStr = insertStr + "'" + trans_dt + "', "
        insertStr = insertStr + "'" + trans_type + "', " 
        insertStr = insertStr + "'" + realized + "', " 
        insertStr = insertStr + trans_amount + ", " 
        insertStr = insertStr + quantity + ", " 
        insertStr = insertStr + "'" + stock_id + "', " 
        insertStr = insertStr + price + ", " 
        insertStr = insertStr + commission + ", " 
        insertStr = insertStr + "'" + account_id + "', " 
        insertStr = insertStr + "'" + account_name + "');"
#        print (insertStr)
        self.purchaseQuery.exec_(insertStr)
        self.model.select()
#        self.model.insertRow(0)
        
    def deleteRecords(self):
        self.model.removeRow(self.ui.tableView.currentIndex().row())

    def filterRecords(self):
        filterString = ""
        if self.ui.accountComboBox.currentIndex() > 0 and self.ui.stockComboBox.currentIndex() > 0:
            filterString = self.accountFilterStrList[self.ui.accountComboBox.currentIndex()] + ' AND ' + self.stockFilterStrList[self.ui.stockComboBox.currentIndex()]
        else:
            if self.ui.accountComboBox.currentIndex() > 0:
                filterString = self.accountFilterStrList[self.ui.accountComboBox.currentIndex()]
            if self.ui.stockComboBox.currentIndex() > 0:
                filterString = self.stockFilterStrList[self.ui.stockComboBox.currentIndex()]
#        print filterString
        self.model.setFilter(filterString)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if not createConnection():
        sys.exit(1)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())

        
