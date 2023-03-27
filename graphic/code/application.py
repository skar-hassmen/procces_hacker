import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QListView, QWidget, QTableView, QMenu, QAction, qApp
import pandas as pd
from PyQt5.QtCore import Qt

from constants import COLUMNS, PATH_MEDIA_FILES
from process_functions import update_process_information
from serializers import serialize_data_for_table


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
        super().__init__()
        self.setWindowTitle("Process Hacker")
        self.setGeometry(300, 250, 1280, 720)
        self.create_table_view()
        self.table_view = None

    def create_table_view(self):
        self.table_view = QTableView()

        json_file = update_process_information()
        data_process = serialize_data_for_table(json_file)
        count_process = len(data_process)

        data_table = pd.DataFrame(data_process, columns=COLUMNS, index=[str(i) for i in range(1, count_process + 1)])

        model_table = TableModel(data_table)
        self.table_view.setModel(model_table)
        self.setCentralWidget(self.table_view)

    def create_menu_bar(self):
        refresh_action = QAction(QIcon(f'{PATH_MEDIA_FILES}/refresh.png'), '&Refresh', self)
        refresh_action.setShortcut('Ctrl+U')
        refresh_action.triggered.connect(self.create_table_view)

        menu_bar = self.menuBar()
        menu_bar.addAction(refresh_action)


def application():
    app = QApplication(sys.argv)
    window = Window()
    window.create_menu_bar()
    window.show()
    sys.exit(app.exec_())
