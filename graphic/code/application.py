import sys
import pandas as pd

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction
from PyQt5.QtCore import Qt

from DataBase import DataBase
from constants import COLUMNS, PATH_MEDIA_FILES, COLUMNS_ADDITIONAL_TABLE, COLUMN_DLL, COLUMN_PRIVILEGES
from serializers import serialize_data_for_table, serialize_additional_info, serialize_list_dlls, \
    serialize_list_privileges


class AdditionalWindow(QMainWindow):
    def __init__(self, name_process, json_file, index):
        super(AdditionalWindow, self).__init__()
        self.name_process = name_process
        self.json_file = json_file
        self.index = index
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(self.name_process)
        width = 700
        height = 750
        self.setGeometry(300, 250, width, height)
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.setEnabled(True)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, width, height))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.create_table_with_additional_info()
        self.create_table_with_dlls()
        self.create_table_with_privileges()

        self.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(self)

    def create_table_with_additional_info(self):
        self.additional_table = QtWidgets.QTableView(self.verticalLayoutWidget)

        self.additional_table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        additional_info = serialize_additional_info(self.json_file, self.index)
        count_process = len(additional_info)
        data_table = pd.DataFrame(additional_info, columns=COLUMNS_ADDITIONAL_TABLE,
                                  index=[str(i) for i in range(1, count_process + 1)])

        header_h = self.additional_table.horizontalHeader()
        header_h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        header_v = self.additional_table.verticalHeader()
        header_v.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        model_table = TableModel(data_table)
        self.additional_table.setModel(model_table)

        self.additional_table.setObjectName("additional_table")
        self.verticalLayout.addWidget(self.additional_table)

    def create_table_with_dlls(self):
        self.dlls_table = QtWidgets.QTableView(self.verticalLayoutWidget)

        self.dlls_table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        dlls_info = serialize_list_dlls(self.json_file, self.index)
        count_dll = len(dlls_info)
        data_table = pd.DataFrame(dlls_info, columns=COLUMN_DLL,
                                  index=[str(i) for i in range(1, count_dll + 1)])

        header_h = self.dlls_table.horizontalHeader()
        header_h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        header_v = self.dlls_table.verticalHeader()
        header_v.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        model_table = TableModel(data_table)
        self.dlls_table.setModel(model_table)

        self.dlls_table.setObjectName("dlls_table")
        self.verticalLayout.addWidget(self.dlls_table)

    def create_table_with_privileges(self):
        self.privileges_table = QtWidgets.QTableView(self.verticalLayoutWidget)

        self.privileges_table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        privileges_info = serialize_list_privileges(self.json_file, self.index)
        count_privileges = len(privileges_info)
        data_table = pd.DataFrame(privileges_info, columns=COLUMN_PRIVILEGES,
                                  index=[str(i) for i in range(1, count_privileges + 1)])

        header_h = self.privileges_table.horizontalHeader()
        header_h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        header_v = self.privileges_table.verticalHeader()
        header_v.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        model_table = TableModel(data_table)
        self.privileges_table.setModel(model_table)

        self.privileges_table.setObjectName("privileges_table")
        self.verticalLayout.addWidget(self.privileges_table)


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

        self.table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        data_process = serialize_data_for_table(self.db.json_array)
        count_process = len(data_process)
        data_table = pd.DataFrame(data_process, columns=COLUMNS, index=[str(i) for i in range(1, count_process + 1)])

        model_table = TableModel(data_table)

        header_h = self.table.horizontalHeader()
        header_h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        header_v = self.table.verticalHeader()
        header_v.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.table.setModel(model_table)
        self.setCentralWidget(self.table)

    def create_menu_bar(self):
        refresh_action = QAction(QIcon(f'{PATH_MEDIA_FILES}/refresh.png'), '&Refresh', self)
        refresh_action.setShortcut('Ctrl+U')
        refresh_action.triggered.connect(self.refresh_table)

        file_owner_action = QAction('&Сhange File Owner', self)
        file_owner_action.setShortcut('Ctrl+O')
        file_owner_action.triggered.connect(self.change_file_owner)

        menu_bar = self.menuBar()
        menu_bar.addAction(refresh_action)

        action_menu = menu_bar.addMenu("&Action")
        action_menu.addAction(file_owner_action)

    def refresh_table(self):
        self.db.update_process_information()
        self.create_table()

    def change_file_owner(self):
        print("777")


def application():
    app = QApplication(sys.argv)

    window = Window()
    window.db.update_process_information()
    window.create_table()
    window.create_menu_bar()

    window.show()
    sys.exit(app.exec_())
