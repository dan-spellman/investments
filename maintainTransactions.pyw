import sys
import pprint
from showTransactions import *
from PyQt4 import QtSql, QtGui, QtCore

pp = pprint.PrettyPrinter(indent=4)

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
        self.ui.dateEdit.setDate(QtCore.QDate().currentDate())
        self.ui.updateButton.clicked.connect(self.updateRecords)
        self.ui.cancelButton.clicked.connect(self.cancelChanges)
        self.ui.addButton.clicked.connect(self.insertRecords)
        self.ui.deleteButton.clicked.connect(self.deleteRecords)
        self.ui.filterButton.clicked.connect(self.filterRecords)
        self.ui.closeButton.clicked.connect(self.closePosition)
        self.ui.transAmountLineEdit.returnPressed.connect(self.findMissingValue)
        self.ui.quantityLineEdit.returnPressed.connect(self.findMissingValue)
        self.ui.priceLineEdit.returnPressed.connect(self.findMissingValue)
        self.ui.commissionLineEdit.returnPressed.connect(self.findMissingValue)

    def findMissingValue(self):
        trans_amount_str = self.ui.transAmountLineEdit.text()
        quantity_str = self.ui.quantityLineEdit.text()
        price_str = self.ui.priceLineEdit.text()
        commission_str = self.ui.commissionLineEdit.text()
        trans_amount = trans_amount_str.toFloat()
        quantity = quantity_str.toFloat()
        price = price_str.toFloat()
        commission = commission_str.toFloat()
        if trans_amount[1] and quantity[1] and price[1] and not commission[1]:
            new_commission = trans_amount[0] + quantity[0] * price[0]
            self.ui.commissionLineEdit.setText("%.2f"%new_commission)
        if trans_amount[1] and quantity[1] and not price[1] and commission[1]:
            if quantity[0] == 0.0:
                new_price = 0.0
            else:
                new_price = (commission[0] - trans_amount[0]) / quantity[0]
            self.ui.priceLineEdit.setText("%.4f"%new_price)
        if trans_amount[1] and not quantity[1] and price[1] and commission[1]:
            if price_str[0] == 0.0:
                new_quantity = 0.0
            else:
                new_quantity = (commission[0] - trans_amount[0]) / price[0]
            self.ui.quantityLineEdit.setText("%.0f"%new_quantity)
        if not trans_amount[1] and quantity[1] and price[1] and commission[1]:
            new_trans_amount = commission[0] - (quantity[0] * price[0])
            self.ui.transAmountLineEdit.setText("%.2f"%new_trans_amount)


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
        stock_id_dict = {}
        while self.purchaseQuery.next():
            stock_id=self.purchaseQuery.value(0).toString()
            if len(stock_id) > 0:
                if len(stock_id) < 5:
                    st_id = stock_id
                else:
                    st_id = stock_id.split(" ")[0]
                if st_id not in stock_id_dict:
                    # stock_id_dict[st_id] = "stock_id LIKE %s%%"%st_id
                    stock_id_dict[st_id] = 'stock_id LIKE "%s%%"'%st_id
        # pp.pprint(stock_id_dict)
        for key in sorted(stock_id_dict):
            self.ui.stockComboBox.addItem(key)
            self.stockFilterStrList.append(stock_id_dict[key])
        pp.pprint(self.stockFilterStrList)

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
        print filterString
        self.model.setFilter(filterString)

    def closePosition(self):
        current_row = self.ui.tableView.currentIndex().row()
        self.ui.tableView.selectRow(current_row)
        quantity = self.model.record(current_row).value("quantity").toInt()[0]
        close_quantity = -1 * quantity
        close_quantity_str = "%d"%close_quantity
        trans_type = self.model.record(current_row).value("trans_type").toString()
        stock_id = self.model.record(current_row).value("stock_id").toString()
        account_id = self.model.record(current_row).value("account_id").toString()
        buy_index = self.ui.transTypeComboBox.findText('BUY', QtCore.Qt.MatchFixedString)
        sell_index = self.ui.transTypeComboBox.findText('SELL', QtCore.Qt.MatchFixedString)
        if trans_type == "BUY":
            self.ui.transTypeComboBox.setCurrentIndex(sell_index)
        if trans_type == "SELL":
            self.ui.transTypeComboBox.setCurrentIndex(buy_index)
        realized_index = self.ui.realizedComboBox.findText('REALIZED', QtCore.Qt.MatchFixedString)
        self.ui.realizedComboBox.setCurrentIndex(realized_index)
        self.ui.quantityLineEdit.setText(close_quantity_str)
        self.ui.stockIdLineEdit.setText(stock_id)
        account_index = self.ui.accountIdComboBox.findText(account_id, QtCore.Qt.MatchFixedString)
        self.ui.accountIdComboBox.setCurrentIndex(account_index)
#        print "Closing position at index: %d"%current_index

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if not createConnection():
        sys.exit(1)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
