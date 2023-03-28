import sys
import pandas as pd

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction
from PyQt5.QtCore import Qt

from DataBase import DataBase
from constants import COLUMNS, PATH_MEDIA_FILES, COLUMN_ADDITIONAL_TABLE
from serializers import serialize_data_for_table, serialize_additional_info


class AdditionalWindow(QMainWindow):
    def __init__(self, name_process, json_file, index):
        super(AdditionalWindow, self).__init__()
        self.name_process = name_process
        self.json_file = json_file
        self.index = index
        self.data_process = None
        self.setupUi()

    def setupUi(self):
        self.data_process = serialize_additional_info(self.json_file, self.index)

        self.setWindowTitle(self.name_process)
        self.setGeometry(300, 250, 800, 600)
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.setEnabled(True)
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 801, 601))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.additional_table = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.additional_table.setFixedSize(800, 90)

        header = self.additional_table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        additional_info = [self.data_process[0], self.data_process[1], self.data_process[2], self.data_process[3]]
        data_table = pd.DataFrame([additional_info], columns=COLUMN_ADDITIONAL_TABLE, index=[1])

        model_table = TableModel(data_table)
        self.additional_table.setModel(model_table)

        self.additional_table.setObjectName("additional_table")
        self.verticalLayout.addWidget(self.additional_table)
        self.list_dll = QtWidgets.QListWidget(self.verticalLayoutWidget)

        self.list_dll.setObjectName("list_dll")
        for _ in self.data_process[4]:
            item = QtWidgets.QListWidgetItem()
            self.list_dll.addItem(item)

        self.verticalLayout.addWidget(self.list_dll)
        self.list_privileges = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.list_privileges.setObjectName("list_privileges")

        for _ in self.data_process[5]:
            item = QtWidgets.QListWidgetItem()
            self.list_privileges.addItem(item)

        self.verticalLayout.addWidget(self.list_privileges)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        __sortingEnabled = self.list_dll.isSortingEnabled()
        self.list_dll.setSortingEnabled(False)

        for ind, elem in enumerate(self.data_process[4]):
            item = self.list_dll.item(ind)
            item.setText(elem)

        self.list_dll.setSortingEnabled(__sortingEnabled)
        __sortingEnabled = self.list_privileges.isSortingEnabled()
        self.list_privileges.setSortingEnabled(False)

        for ind, elem in enumerate(self.data_process[5]):
            item = self.list_privileges.item(ind)
            item.setText(elem)

        self.list_privileges.setSortingEnabled(__sortingEnabled)


class MyTableView(QtWidgets.QTableView):
    def __init__(self, main_window):
        super(MyTableView, self).__init__()
        self.main_window = main_window

    def mouseDoubleClickEvent(self, event):
        index = self.currentIndex().siblingAtColumn(0)
        name_process = index.data()

        self.additional_window = AdditionalWindow(name_process, self.main_window.db.json_array, index.row())
        self.additional_window.show()


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Process Hacker")
        self.setGeometry(300, 250, 1280, 720)
        icon = QIcon(f'{PATH_MEDIA_FILES}/spy.png')
        self.setWindowIcon(icon)
        self.table = None
        self.db = DataBase()
        self.additional_window = None

    def create_table(self):
        self.table = MyTableView(self)

        data_process = serialize_data_for_table(self.db.json_array)
        count_process = len(data_process)
        data_table = pd.DataFrame(data_process, columns=COLUMNS, index=[str(i) for i in range(1, count_process + 1)])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        model_table = TableModel(data_table)
        self.table.setModel(model_table)
        self.setCentralWidget(self.table)

    def create_menu_bar(self):
        refresh_action = QAction(QIcon(f'{PATH_MEDIA_FILES}/refresh.png'), '&Refresh', self)
        refresh_action.setShortcut('Ctrl+U')
        refresh_action.triggered.connect(self.refresh_table)

        menu_bar = self.menuBar()
        menu_bar.addAction(refresh_action)

    def refresh_table(self):
        self.db.update_process_information()
        self.create_table()




def application():
    app = QApplication(sys.argv)

    window = Window()
    window.db.update_process_information()
    window.create_table()
    window.create_menu_bar()

    window.show()
    sys.exit(app.exec_())
