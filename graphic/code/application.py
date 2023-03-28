import sys
import pandas as pd

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QListView, QWidget, QTableView, QMenu, QAction, \
    qApp, QLabel, QListWidget
from PyQt5.QtCore import Qt

from DataBase import DataBase
from constants import COLUMNS, PATH_MEDIA_FILES
from serializers import serialize_data_for_table, serialize_additional_info


class AdditionalWindow(QWidget):
    def __init__(self, name_process):
        super(AdditionalWindow, self).__init__()
        self.setWindowTitle(name_process)
        self.setGeometry(300, 250, 800, 600)
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

    def create_additional_info(self, json_array, index):
        data_process = serialize_additional_info(json_array, index)

        path_exe = QLabel(self)
        path_exe.setText(f"Path exe: {data_process[0]}")
        path_exe.move(50, 50)
        path_exe.adjustSize()

        ASLR_EnableBottomUpRandomization = QLabel(self)
        ASLR_EnableBottomUpRandomization.setText(f"ASLR EnableBottomUpRandomization: {data_process[1]}")
        ASLR_EnableBottomUpRandomization.move(50, 70)
        ASLR_EnableBottomUpRandomization.adjustSize()

        ASLR_EnableForceRelocateImages = QLabel(self)
        ASLR_EnableForceRelocateImages.setText(f"ASLR EnableForceRelocateImages: {data_process[2]}")
        ASLR_EnableForceRelocateImages.move(50, 90)
        ASLR_EnableForceRelocateImages.adjustSize()

        ASLR_EnableHighEntropy = QLabel(self)
        ASLR_EnableHighEntropy.setText(f"ASLR EnableHighEntropy: {data_process[3]}")
        ASLR_EnableHighEntropy.move(50, 110)
        ASLR_EnableHighEntropy.adjustSize()

        dll_list = QLabel(self)
        dll_list.setText(f"DLL: ")
        dll_list.move(50, 130)
        dll_list.adjustSize()


        n = 0
        if data_process[5] == "No data":
            ASLR_EnableHighEntropy = QLabel(self)
            ASLR_EnableHighEntropy.setText("No data")
            ASLR_EnableHighEntropy.move(50, 140)
            n += 10
            ASLR_EnableHighEntropy.adjustSize()
        else:
            for elem in data_process[4]:
                n += 10
                ASLR_EnableHighEntropy = QLabel(self)
                ASLR_EnableHighEntropy.setText(f"{elem}")
                ASLR_EnableHighEntropy.move(50, 130 + n)
                ASLR_EnableHighEntropy.adjustSize()

        dll_list = QLabel(self)
        dll_list.setText(f"Privileges: ")
        dll_list.move(50, 130 + n + 10)
        dll_list.adjustSize()

        m = 0
        if data_process[5] == "No data":
            ASLR_EnableHighEntropy = QLabel(self)
            ASLR_EnableHighEntropy.setText("No data")
            ASLR_EnableHighEntropy.move(50, 130 + n + m + 10 + 10)
            ASLR_EnableHighEntropy.adjustSize()
        else:
            for elem in data_process[5]:
                m += 10
                ASLR_EnableHighEntropy = QLabel(self)
                ASLR_EnableHighEntropy.setText(f"{elem}")
                ASLR_EnableHighEntropy.move(50, 130 + n + m + 10)
                ASLR_EnableHighEntropy.adjustSize()



class MyTableView(QtWidgets.QTableView):
    def __init__(self, main_window):
        super(MyTableView, self).__init__()
        self.main_window = main_window

    def mouseDoubleClickEvent(self, event):
        index = self.currentIndex().siblingAtColumn(0)
        name_process = index.data()
        self.additional_window = AdditionalWindow(name_process)
        self.additional_window.create_additional_info(self.main_window.db.json_array, index.row())
        self.additional_window.show()
        print(index.row())


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
