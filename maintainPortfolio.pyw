import sys
from showPortfolio import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtSql
from googlefinance import getQuotes
from yahoo_finance import Share
from alpha_vantage.timeseries import TimeSeries
from scipy import optimize
from datetime import datetime, date, time
import locale
import time

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
        self.longModel = QStandardItemModel()
        self.ui.longView.setModel(self.longModel)
        self.ui.longView.sortByColumn(0)
        self.shortModel = QStandardItemModel()
        self.ui.shortView.setModel(self.shortModel)
        self.ui.shortView.sortByColumn(0)
        self.optionModel = QStandardItemModel()
        self.ui.optionView.setModel(self.optionModel)
        self.ui.optionView.sortByColumn(0)
        self.purchaseQuery = QtSql.QSqlQuery()
        self.stockQuery = QtSql.QSqlQuery()
        self.depositWithdrawalQuery = QtSql.QSqlQuery()
        self.getAccounts()
        self.getTransactions()
#        self.updatePrices()
#        self.genStats()
        self.sortOrder="Ascending"
        QtCore.QObject.connect(self.ui.getTransactionsButton, QtCore.SIGNAL('clicked()'),self.getTransactions)
        # QtCore.QObject.connect(self.ui.updatePricesButton, QtCore.SIGNAL('clicked()'),self.updatePricesGoogle)
        QtCore.QObject.connect(self.ui.updatePricesButton, QtCore.SIGNAL('clicked()'),self.updatePricesAlphaVantage)
        QtCore.QObject.connect(self.ui.genStatsButton, QtCore.SIGNAL('clicked()'),self.genStats)
        QtCore.QObject.connect(self.ui.longView.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'),self.sortLongView)
        QtCore.QObject.connect(self.ui.shortView.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'),self.sortShortView)
        QtCore.QObject.connect(self.ui.optionView.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'),self.sortOptionView)

    def getAccounts(self):
        print ("Getting Accounts")
        self.ui.accountComboBox.addItem("ALL")
        self.filterStrList = [""]
        self.purchaseQuery.exec_("SELECT DISTINCT account_id FROM transactions")
        while self.purchaseQuery.next():
            account_id=self.purchaseQuery.value(0).toString()
            self.ui.accountComboBox.addItem(account_id)
            filterStr = (" AND account_id = '%s'" %account_id)
            self.filterStrList.append(filterStr)

    def getTransactions(self):
        print ("Getting Transactions")
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='DEPOSIT'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_deposits=self.purchaseQuery.value(0).toFloat()[0]
        depositStr = "$" + "{:,.2f}".format(self.total_deposits)
        print("total deposits = %s" %depositStr)
        self.ui.depositLineEdit.setText(depositStr)
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='WITHDRAWAL'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_withdrawals=self.purchaseQuery.value(0).toFloat()[0]
        withdrawalStr = "$" + "{:,.2f}".format(self.total_withdrawals)
        print("total withdrawals = %s" %withdrawalStr)
        self.ui.withdrawalLineEdit.setText(withdrawalStr)
        self.net_deposits=self.total_deposits+self.total_withdrawals
        netStr = "$" + "{:,.2f}".format(self.net_deposits)
        print("net deposits = %s" %netStr)
        self.ui.netLineEdit.setText(netStr)
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='BUY'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_purchase=self.purchaseQuery.value(0).toFloat()[0]
        purchaseStr = "$" + "{:,.2f}".format(self.total_purchase)
        print("total purchases = %s" %purchaseStr)
        self.ui.purchasesLineEdit.setText(purchaseStr)
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='SELL'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_sale=self.purchaseQuery.value(0).toFloat()[0]
        saleStr = "$" + "{:,.2f}".format(self.total_sale)
        print("total sales = %s" %saleStr)
        self.ui.salesLineEdit.setText(saleStr)
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='DIVIDEND'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_dividends=self.purchaseQuery.value(0).toFloat()[0]
        dividendStr = "$" + "{:,.2f}".format(self.total_dividends)
        print("total dividends = %s" %dividendStr)
        self.ui.dividendLineEdit.setText(dividendStr)
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='INTEREST'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_interest=self.purchaseQuery.value(0).toFloat()[0]
        interestStr = "$" + "{:,.2f}".format(self.total_interest)
        print("total interest = %s" %interestStr)
        self.ui.interestLineEdit.setText(interestStr)
        purchaseQueryStr = "SELECT SUM(trans_amount) FROM transactions WHERE trans_type='FEE'" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
        self.purchaseQuery.exec_(purchaseQueryStr)
        self.purchaseQuery.next()
        self.total_fees=self.purchaseQuery.value(0).toFloat()[0]
        feeStr = "$" + "{:,.2f}".format(self.total_fees)
        print("total fees = %s" %feeStr)
        self.ui.feeLineEdit.setText(feeStr)
        self.cash_value = self.total_deposits + self.total_withdrawals + self.total_purchase + self.total_sale + self.total_dividends + self.total_interest + self.total_fees
        cash_value_str = "$" + "{:,.2f}".format(self.cash_value)
        print("cash on hand = %s" %cash_value_str)
        self.ui.cashValueLineEdit.setText(cash_value_str)
        self.longModel.clear()
        self.longModel.setHorizontalHeaderLabels(["Ticker","Shares","Current Price","Buy Price","Buy Date","Return(%)","Market Value","Unrealized Gain","Port(%)","Allocation(%)","Over/Under(%)","Over/Under(shares)"])
        self.shortModel.clear()
        self.shortModel.setHorizontalHeaderLabels(["Ticker","Shares","Current Price","Sell Price","Sell Date","Return(%)","Market Value","Unrealized Gain","Port(%)","Allocation(%)","Over/Under(%)","Over/Under(shares)"])
        self.optionModel.clear()
        self.optionModel.setHorizontalHeaderLabels(["Ticker","Contracts","Contract Price","Total Price","Contract Date","Company","Strategy","Expiration","Strike Price","Equity Price"])
        longRowIndex = 0
        shortRowIndex = 0
        optionRowIndex = 0
#        stockValue = 0.0
        purchaseQueryStr = "SELECT DISTINCT stock_id FROM transactions WHERE (trans_type = 'BUY' OR trans_type = 'SELL')" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
#        print(purchaseQueryStr)
        self.purchaseQuery.exec_(purchaseQueryStr)
        while self.purchaseQuery.next():
            ticker=self.purchaseQuery.value(0).toString()
#            print("stock_id: %s" %ticker)
            if ticker.length() <= 5: #ticker is for a stock; greater than 4 indicates an option
                baseQuery = "SELECT MIN(trans_dt), SUM(trans_amount), SUM(quantity), SUM(commission) FROM transactions"
                queryFilter = " WHERE realized = '0' AND (trans_type = 'BUY' OR trans_type = 'SELL')" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
#                queryFilter = " WHERE (trans_type = 'BUY' OR trans_type = 'SELL')" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
                qStockQuery = baseQuery + queryFilter + (" AND stock_id='%s'" %ticker)  + self.filterStrList[self.ui.accountComboBox.currentIndex()]
#                print (qStockQuery)
                self.stockQuery.exec_(qStockQuery)
                self.stockQuery.next()
                total_shares=self.stockQuery.value(2).toFloat()[0]
                buy_date=self.stockQuery.value(0).toString()
                total_price=self.stockQuery.value(1).toFloat()[0]
                total_commision=self.stockQuery.value(3).toFloat()[0]
                tickerItem = QStandardItem(ticker)
                tickerItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                totalStaresItem = QStandardItem("%7.0f" %total_shares)
                totalStaresItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if total_shares != 0:
                    avg_price = total_price/total_shares*-1.0
                    avgPriceItem = QStandardItem("$%7.2f" %avg_price)
                    avgPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if total_shares > 0: #positive shares indicate a long position
                    self.longModel.setItem(longRowIndex, 0, tickerItem)
                    self.longModel.setItem(longRowIndex, 1, totalStaresItem)
                    self.longModel.setItem(longRowIndex, 3, avgPriceItem)
                    self.longModel.setItem(longRowIndex, 4, QStandardItem(buy_date))
                    longRowIndex += 1
                if total_shares < 0: #negative shares indicate a short position
                    self.shortModel.setItem(shortRowIndex, 0, tickerItem)
                    self.shortModel.setItem(shortRowIndex, 1, totalStaresItem)
                    self.shortModel.setItem(shortRowIndex, 3, avgPriceItem)
                    self.shortModel.setItem(shortRowIndex, 4, QStandardItem(buy_date))
                    shortRowIndex += 1
            else: #ticker is for an option
                baseQuery = "SELECT MIN(trans_dt), SUM(trans_amount), SUM(quantity), SUM(commission) FROM transactions"
                queryFilter = " WHERE (trans_type = 'BUY' OR trans_type = 'SELL')" + self.filterStrList[self.ui.accountComboBox.currentIndex()]
                qStockQuery = baseQuery + queryFilter + (" AND stock_id='%s'" %ticker)  + self.filterStrList[self.ui.accountComboBox.currentIndex()]
#                print (qStockQuery)
                self.stockQuery.exec_(qStockQuery)
                self.stockQuery.next()
                total_contracts=self.stockQuery.value(2).toFloat()[0]
                contract_date=self.stockQuery.value(0).toString()
                total_price=self.stockQuery.value(1).toFloat()[0]
                total_commision=self.stockQuery.value(3).toFloat()[0]
                tickerItem = QStandardItem(ticker)
                tickerItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                totalContractsItem = QStandardItem("%7.0f" %total_contracts)
                totalContractsItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if total_contracts != 0:
                    totalPriceItem = QStandardItem("$%7.2f" %total_price)
                    totalPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    avg_price = total_price/total_contracts*-1.0
                    avgPriceItem = QStandardItem("$%7.2f" %avg_price)
                    avgPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    ticker_elements = ticker.split(" ")
                    strategy_code = ticker_elements[1][6]
                    if strategy_code == "P":
                        strategy = "PUT"
                    elif strategy_code == "C":
                        strategy = "CALL"
                    else:
                        strategy = "UNKNOWN"
                    expiration_date = "20" + ticker_elements[1][0:2] + "-" + ticker_elements[1][2:4] + "-" + ticker_elements[1][4:6]
                    strike_price = float(ticker_elements[1][7:]) / 100
                    strike_price_element = QStandardItem("$%7.2f" %strike_price)
                    self.optionModel.setItem(optionRowIndex, 0, tickerItem)
                    self.optionModel.setItem(optionRowIndex, 1, totalContractsItem)
                    self.optionModel.setItem(optionRowIndex, 2, avgPriceItem)
                    self.optionModel.setItem(optionRowIndex, 3, totalPriceItem)
                    self.optionModel.setItem(optionRowIndex, 4, QStandardItem(contract_date))
                    self.optionModel.setItem(optionRowIndex, 5, QStandardItem(ticker_elements[0]))
                    self.optionModel.setItem(optionRowIndex, 6, QStandardItem(strategy))
                    self.optionModel.setItem(optionRowIndex, 7, QStandardItem(expiration_date))
                    self.optionModel.setItem(optionRowIndex, 8, strike_price_element)
                    optionRowIndex += 1
            self.ui.longView.resizeColumnsToContents()
            self.ui.shortView.resizeColumnsToContents()
            self.ui.optionView.resizeColumnsToContents()
        self.ui.longView.sortByColumn(0,0)
        self.ui.shortView.sortByColumn(0,0)

    def updatePricesGoogle(self):
        print ("Updating Prices from Google")
        locale.setlocale(locale.LC_NUMERIC, '')
        tickerSet = set()
        # Get ticker symbols from long table
        numRows=self.longModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.longModel.item(rowIndex,0).text())
#            print (ticker)
            tickerSet.add(ticker)
            rowIndex += 1
        # Get ticker symbols from Short table
        numRows=self.shortModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.shortModel.item(rowIndex,0).text())
#            print (ticker)
            tickerSet.add(ticker)
            rowIndex += 1
        # Get ticker symbols from Options table
        numRows=self.optionModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.optionModel.item(rowIndex,5).text())
#            print (ticker)
            tickerSet.add(ticker)
            rowIndex += 1
        tickerList = list(tickerSet)
#        print (tickerList)
        googleQuotes = getQuotes(tickerList)
##        print (googleQuotes)
        # Update current prices in Long Table
        numRows=self.longModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.longModel.item(rowIndex,0).text())
            quoteNotFound = True
            for quote in googleQuotes:
                if quote['StockSymbol'] == ticker:
                    quoteNotFound = False
                    curr_price=locale.atof(quote['LastTradePrice'])
                    currPriceItem = QStandardItem("$%7.2f" %curr_price)
                    currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
                    self.longModel.setItem(rowIndex, 2, currPriceItem)
                    break
            if quoteNotFound:
                print ("A quote was not found for %s" %ticker)
                print (googleQuotes)
            rowIndex += 1
        self.ui.longView.resizeColumnsToContents()
        # Update current prices in Short Table
        numRows=self.shortModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.shortModel.item(rowIndex,0).text())
            quoteNotFound = True
            for quote in googleQuotes:
                if quote['StockSymbol'] == ticker:
                    quoteNotFound = False
                    curr_price=float(quote['LastTradePrice'])
                    currPriceItem = QStandardItem("$%7.2f" %curr_price)
                    currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
                    self.shortModel.setItem(rowIndex, 2, currPriceItem)
                    break
            if quoteNotFound:
                print ("A quote was not found for %s" %ticker)
                print (googleQuotes)
            rowIndex += 1
        self.ui.shortView.resizeColumnsToContents()
        # Update current prices in Optioins Table
        numRows=self.optionModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.optionModel.item(rowIndex,5).text())
            quoteNotFound = True
            for quote in googleQuotes:
                if quote['StockSymbol'] == ticker:
                    quoteNotFound = False
                    curr_price=float(quote['LastTradePrice'])
                    currPriceItem = QStandardItem("$%7.2f" %curr_price)
                    currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
                    self.optionModel.setItem(rowIndex, 9, currPriceItem)
                    break
            if quoteNotFound:
                print ("A quote was not found for %s" %ticker)
                print (googleQuotes)
            rowIndex += 1
        self.ui.shortView.resizeColumnsToContents()

    def updatePricesYahoo(self):
        print ("Updating Prices from Yahoo")
        locale.setlocale(locale.LC_NUMERIC, '')
        # Update current prices in Long Table
        numRows=self.longModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.longModel.item(rowIndex,0).text())
            stock = Share(ticker)
            curr_price=locale.atof(stock.get_price())
            currPriceItem = QStandardItem("$%7.2f" %curr_price)
            currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
            self.longModel.setItem(rowIndex, 2, currPriceItem)
            rowIndex += 1
        self.ui.longView.resizeColumnsToContents()
        # Update current prices in Short Table
        numRows=self.shortModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.shortModel.item(rowIndex,0).text())
            stock = Share(ticker)
            curr_price=locale.atof(stock.get_price())
            currPriceItem = QStandardItem("$%7.2f" %curr_price)
            currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
            self.shortModel.setItem(rowIndex, 2, currPriceItem)
            rowIndex += 1
        self.ui.shortView.resizeColumnsToContents()
        # Update current prices in Optioins Table
        numRows=self.optionModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.optionModel.item(rowIndex,5).text())
            stock = Share(ticker)
            curr_price=locale.atof(stock.get_price())
            currPriceItem = QStandardItem("$%7.2f" %curr_price)
            currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
            self.optionModel.setItem(rowIndex, 9, currPriceItem)
            rowIndex += 1
        self.ui.optionView.resizeColumnsToContents()

    def updatePricesAlphaVantage(self):
        print ("Updating Prices from Alpha Vantage")
        locale.setlocale(locale.LC_NUMERIC, '')
        ts = TimeSeries(key='QLVWW4KKUV0NVWPP')
        # Update current prices in Long Table
        numRows=self.longModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.longModel.item(rowIndex,0).text())
            try:
                data,meta_data = ts.get_daily(symbol=ticker)
                latest_date = max(data.keys())
                curr_price = locale.atof(data[latest_date]['4. close'])
            except:
                curr_price = "0.00"
            currPriceItem = QStandardItem("$%7.2f" %curr_price)
            currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
            self.longModel.setItem(rowIndex, 2, currPriceItem)
            rowIndex += 1
        self.ui.longView.resizeColumnsToContents()
        # Update current prices in Short Table
        numRows=self.shortModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.shortModel.item(rowIndex,0).text())
            try:
                data,meta_data = ts.get_daily(symbol=ticker)
                latest_date = max(data.keys())
                curr_price = locale.atof(data[latest_date]['4. close'])
            except:
                curr_price = "0.00"
            currPriceItem = QStandardItem("$%7.2f" %curr_price)
            currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
            self.shortModel.setItem(rowIndex, 2, currPriceItem)
            rowIndex += 1
        self.ui.shortView.resizeColumnsToContents()
        # Update current prices in Optioins Table
        numRows=self.optionModel.rowCount()
        rowIndex=0
        while rowIndex < numRows:
            ticker=str(self.optionModel.item(rowIndex,5).text())
            try:
                data,meta_data = ts.get_daily(symbol=ticker)
                latest_date = max(data.keys())
                curr_price = locale.atof(data[latest_date]['4. close'])
            except:
                curr_price = "0.00"
            currPriceItem = QStandardItem("$%7.2f" %curr_price)
            currPriceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            print ("symbol: %s price: %s" %(ticker,currPriceItem.text()))
            self.optionModel.setItem(rowIndex, 9, currPriceItem)
            rowIndex += 1
        self.ui.optionView.resizeColumnsToContents()


    def genStats(self):
        print ("Generating Statistics")
        stockValue = 0.0
        numRows=self.longModel.rowCount()
        rowIndex = 0
        while rowIndex < numRows:
            if self.longModel.item(rowIndex,2) is None:
                curr_price=0.0
            else:
                curr_price=float(self.longModel.item(rowIndex,2).text()[1:])
            buy_price=float(self.longModel.item(rowIndex,3).text()[1:])
            quantity=float(self.longModel.item(rowIndex,1).text())
            if buy_price != 0:
                appreciation = (curr_price/buy_price - 1) *100
            else:
                appreciation = 0.0
            appreciationItem = QStandardItem("%7.1f" %appreciation)
            appreciationItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if appreciation < 0.0:
                appreciationItem.setBackground(QBrush(Qt.red))
            self.longModel.setItem(rowIndex, 5, appreciationItem)
            marketValue = curr_price*quantity
            stockValue += marketValue
            marketValueItem = QStandardItem("$%8.2f" %marketValue)
            marketValueItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.longModel.setItem(rowIndex, 6, marketValueItem)
            unrealizedGain = (curr_price-buy_price)*quantity
            unrealizedGainItem = QStandardItem("$%8.2f" %unrealizedGain)
            unrealizedGainItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if unrealizedGain < 0.0:
                unrealizedGainItem.setBackground(QBrush(Qt.red))
            self.longModel.setItem(rowIndex, 7, unrealizedGainItem)
            rowIndex += 1
        self.ui.longView.resizeColumnsToContents()
        numRows=self.shortModel.rowCount()
        rowIndex = 0
        while rowIndex < numRows:
            if self.shortModel.item(rowIndex,2) is None:
                curr_price=0.0
            else:
                curr_price=float(self.shortModel.item(rowIndex,2).text()[1:])
            sell_price=float(self.shortModel.item(rowIndex,3).text()[1:])
            quantity=float(self.shortModel.item(rowIndex,1).text())
            if curr_price != 0:
                appreciation = (sell_price/curr_price - 1) *100
            else:
                appreciation = 0.0
            appreciationItem = QStandardItem("%7.1f" %appreciation)
            appreciationItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if appreciation < 0.0:
                appreciationItem.setBackground(QBrush(Qt.red))
            self.shortModel.setItem(rowIndex, 5, appreciationItem)
            marketValue = curr_price*quantity
            stockValue += marketValue
            marketValueItem = QStandardItem("$%8.2f" %marketValue)
            marketValueItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.shortModel.setItem(rowIndex, 6, marketValueItem)
            unrealizedGain = (curr_price-sell_price)*quantity
            unrealizedGainItem = QStandardItem("$%8.2f" %unrealizedGain)
            unrealizedGainItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if unrealizedGain < 0.0:
                unrealizedGainItem.setBackground(QBrush(Qt.red))
            self.shortModel.setItem(rowIndex, 7, unrealizedGainItem)
            rowIndex += 1
        self.ui.shortView.resizeColumnsToContents()
        self.stock_value=stockValue
        stockValueStr = "$" + "{:,.2f}".format(self.stock_value)
        print("Stock Value = %s" %stockValueStr)
        self.ui.stockValueLineEdit.setText(stockValueStr)
        self.port_value = self.stock_value + self.cash_value
        portValueStr = "$" + "{:,.2f}".format(self.port_value)
        print("Portfolio Value = %s" %portValueStr)
        self.ui.portValueLineEdit.setText(portValueStr)
        if self.total_deposits != 0:
            self.port_return = ((self.port_value / (self.total_deposits+self.total_withdrawals)) - 1) * 100
        else:
            self.port_return = 0.0
        portReturnStr = "{:,.2f}".format(self.port_return) + "%"
        self.ui.absReturnLineEdit.setText(portReturnStr)
        if self.port_value != 0:
            self.cash_position = (self.cash_value / self.port_value) * 100
            self.stock_position = (self.stock_value / self.port_value) * 100
        else:
            self.cash_position = 0.0
            self.stock_position = 0.0
        cashPositionStr = "{:,.2f}".format(self.cash_position) + "%"
        self.ui.cashPositionLineEdit.setText(cashPositionStr)
        stockPositionStr = "{:,.2f}".format(self.stock_position) + "%"
        self.ui.stockPositionLineEdit.setText(stockPositionStr)
        numRows=self.longModel.rowCount()
        rowIndex = 0
        while rowIndex < numRows:
            market_value=float(self.longModel.item(rowIndex,6).text()[1:])
            if self.port_value != 0:
                port_position=(market_value/self.port_value) *100
            else:
                port_position=0.0
            positionItem = QStandardItem("%7.2f" %port_position)
            positionItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.longModel.setItem(rowIndex, 8, positionItem)
            rowIndex += 1
        self.ui.longView.resizeColumnsToContents()
        numRows=self.shortModel.rowCount()
        rowIndex = 0
        while rowIndex < numRows:
            market_value=float(self.shortModel.item(rowIndex,6).text()[1:])
            if self.port_value != 0:
                port_position=(market_value/self.port_value) *-100
            else:
                port_position=0.0
            positionItem = QStandardItem("%7.2f" %port_position)
            positionItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.shortModel.setItem(rowIndex, 8, positionItem)
            rowIndex += 1
        self.ui.shortView.resizeColumnsToContents()
        self.genAllocations()
        self.genXIRR()

    def genAllocations(self):
        print ("Generating Allocations Statistics")
        numRows=self.longModel.rowCount()
        rowIndex = 0
        while rowIndex < numRows:
            ticker=self.longModel.item(rowIndex,0).text()
            curr_price=float(self.longModel.item(rowIndex,2).text()[1:])
            curr_percent=float(self.longModel.item(rowIndex,8).text())
            baseQuery = ("SELECT allocation FROM allocations WHERE (type = 'LONG' AND stock_id='%s');" %ticker)
            self.stockQuery.exec_(baseQuery)
            self.stockQuery.next()
            allocation=self.stockQuery.value(0).toFloat()[0]
            print ("ticker: %s allocation: %s" %(ticker,allocation))
            allocationItem = QStandardItem("%7.2f" %allocation)
            allocationItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.longModel.setItem(rowIndex, 9, allocationItem)
            overUnderPercent=curr_percent-allocation
            overUnderPercentItem = QStandardItem("%7.2f" %overUnderPercent)
            overUnderPercentItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if abs(overUnderPercent) >= 0.5:
                overUnderPercentItem.setBackground(QBrush(Qt.yellow))
            self.longModel.setItem(rowIndex, 10, overUnderPercentItem)
            overUnderStares=overUnderPercent/100*self.port_value/curr_price
            overUnderStaresItem = QStandardItem("%7.0f" %overUnderStares)
            overUnderStaresItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if abs(overUnderPercent) >= 0.5:
                overUnderStaresItem.setBackground(QBrush(Qt.yellow))
            self.longModel.setItem(rowIndex, 11, overUnderStaresItem)
            rowIndex += 1
        numRows=self.shortModel.rowCount()
        rowIndex = 0
        while rowIndex < numRows:
            ticker=self.shortModel.item(rowIndex,0).text()
            curr_price=float(self.shortModel.item(rowIndex,2).text()[1:])
            curr_percent=float(self.shortModel.item(rowIndex,8).text())
            baseQuery = ("SELECT allocation FROM allocations WHERE (type = 'SHORT' AND stock_id='%s');" %ticker)
            self.stockQuery.exec_(baseQuery)
            self.stockQuery.next()
            allocation=self.stockQuery.value(0).toFloat()[0]
#            print ("ticker: %s allocation: %s" %(ticker,allocation))
            allocationItem = QStandardItem("%7.2f" %allocation)
            allocationItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.shortModel.setItem(rowIndex, 9, allocationItem)
            overUnderPercent=curr_percent-allocation
            overUnderPercentItem = QStandardItem("%7.2f" %overUnderPercent)
            overUnderPercentItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if abs(overUnderPercent) >= 0.5:
                overUnderPercentItem.setBackground(QBrush(Qt.yellow))
            self.shortModel.setItem(rowIndex, 10, overUnderPercentItem)
            overUnderStares=overUnderPercent/100*self.port_value/curr_price
            overUnderStaresItem = QStandardItem("%7.0f" %overUnderStares)
            overUnderStaresItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if abs(overUnderPercent) >= 0.5:
                overUnderStaresItem.setBackground(QBrush(Qt.yellow))
            self.shortModel.setItem(rowIndex, 11, overUnderStaresItem)
            rowIndex += 1

    def genXIRR(self):
        print ("generating XIRR")
        cashflow=self.getDepositsWithdrawals()
        today=datetime.now()
        currentTuple=(today,-self.port_value)
        cashflow.append(currentTuple)
#        print(cashflow)
        xirrReturn=self.xirr(cashflow)
#        print(xirrReturn)
        xirrReturnStr = "{:,.2f}".format(xirrReturn*100.0) + "%"
        self.ui.xirrReturnLineEdit.setText(xirrReturnStr)

    def getDepositsWithdrawals(self):
        print ("getting Deposits and Withdrawals")
        dWList=[]
        self.depositWithdrawalQuery.exec_("SELECT trans_dt, trans_amount FROM transactions WHERE trans_type='DEPOSIT' OR trans_type='WITHDRAWAL'")
        while self.depositWithdrawalQuery.next():
            date=self.depositWithdrawalQuery.value(0).toDateTime().toPyDateTime()
            amount=self.depositWithdrawalQuery.value(1).toFloat()
            dWTuple=(date,amount[0])
            dWList.append(dWTuple)
        return dWList

    def xnpv(self,rate,cashflows):
        """
        Calculate the net present value of a series of cashflows at irregular intervals.
        Arguments
        ---------
        * rate: the discount rate to be applied to the cash flows
        * cashflows: a list object in which each element is a tuple of the form (date, amount),
                       where date is a python datetime.date object and amount is an integer or floating point number.
                       Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.

        Returns
        -------abs
        * returns a single value which is the NPV of the given cash flows.
        Notes
        ---------------
        * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow.
          The discounted value of a given cash flow is A/(1+r)**(t-t0),
          where A is the amount, r is the discout rate,
          and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of the cash flow being added to the sum (t).
        * This function is equivalent to the Microsoft Excel function of the same name.
        """

        chron_order = sorted(cashflows, key = lambda x: x[0])
        t0 = chron_order[0][0] #t0 is the date of the first cash flow

        return sum([cf/(1+rate)**((t-t0).days/365.0) for (t,cf) in chron_order])

    def xirr(self,cashflows,guess=0.1):
        """
        Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.
        Arguments
        ---------
        * cashflows: a list object in which each element is a tuple of the form (date, amount),
                       where date is a python datetime.date object and amount is an integer or floating point number.
                       Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
        * guess (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution.
        Returnsabs
        --------
        * Returns the IRR as a single value

        Notes
        ----------------
        * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV) of a series of cash flows is equal to zero.
            The NPV of the series of cash flows is determined using the xnpv function in this module.
            The discount rate at which NPV equals zero is found using the secant method of numerical solution.
        * This function is equivalent to the Microsoft Excel function of the same name.
        * For users that do not have the scipy module installed, there is an alternate version (commented out) that uses the secant_method function
            defined in the module rather than the scipy.optimize module's numerical solver.
            Both use the same method of calculation so there should be no difference in performance,
            but the secant_method function does not fail gracefully in cases where there is no solution, so the scipy.optimize.newton version is preferred.
        """

        #return secant_method(0.0001,lambda r: xnpv(r,cashflows),guess)
        return optimize.newton(lambda r: self.xnpv(r,cashflows),guess)

    def sortLongView(self, section):
#        print ("Sorting Long View")
#        print (section)
        self.ui.longView.sortByColumn(section)

    def sortShortView(self, section):
#        print ("Sorting Short View")
#        print (section)
        self.ui.shortView.sortByColumn(section)

    def sortOptionView(self, section):
#        print ("Sorting Option View")
#        print (section)
        self.ui.optionView.sortByColumn(section)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if not createConnection():
        sys.exit(1)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
