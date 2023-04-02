import sys
import pandas as pd

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from DataBase import DataBase
from constants import COLUMNS, PATH_MEDIA_FILES, COLUMNS_ADDITIONAL_TABLE, COLUMN_DLL, COLUMN_PRIVILEGES, \
    COLUMN_INTEGRITY, INTEGRITY_LEVELS, INCORRECT_INTEGRITY_LEVELS, PRIVILEGES_CHOSEN, OWNER_CHOSEN
from serializers import serialize_data_for_table, serialize_additional_info, serialize_list_dlls, \
    serialize_list_privileges, serialize_integrity_level


class PrivilegesWindow(QMainWindow):
    def __init__(self, current_privilege, current_privilege_status):
        super(PrivilegesWindow, self).__init__()
        self.current_privilege = current_privilege
        self.current_privilege_status = current_privilege_status
        self.setupUi()

    def setupUi(self):
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(self)

        self.privilege_chosen = QComboBox(self)
        self.privilege_chosen.addItems(PRIVILEGES_CHOSEN)
        self.privilege_chosen.setCurrentText(self.current_privilege_status)
        self.privilege_chosen.move(50, 20)

        button = QPushButton("Change", self)
        button.move(50, 65)
        button.clicked.connect(self.change_status_privilege)

    def change_status_privilege(self):
        new_privilege_status = self.privilege_chosen.currentText()
        if new_privilege_status == self.current_privilege_status:
            self.showDialog({
                'icon': QMessageBox.Information,
                'main_text': 'There were no changes. First change the setting and try again.',
                'title_text': 'Information: There were no changes'
            })
        else:
            db = DataBase()
            db.change_status_privilege(db.json_array[db.current_index]['PID'], self.current_privilege, new_privilege_status)

            self.showDialog({
                'icon': QMessageBox.Information,
                'main_text': 'The data has been successfully changed. Check the status privilege of this process !',
                'title_text': 'Ok: The data has been successfully changed'
            })
            self.close()

    def showDialog(self, params):
        self.integity_msgBox = QMessageBox()
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.integity_msgBox.setWindowIcon(icon)
        self.integity_msgBox.setIcon(params['icon'])
        self.integity_msgBox.setText(params["main_text"])
        self.integity_msgBox.setWindowTitle(params["title_text"])
        self.integity_msgBox.setStandardButtons(QMessageBox.Ok)
        self.integity_msgBox.show()


class PrivilegesTableView(QtWidgets.QTableView):

    def mouseDoubleClickEvent(self, event):
        index1 = self.currentIndex().siblingAtColumn(0)
        index2 = self.currentIndex().siblingAtColumn(1)
        current_privilege = index1.data()
        current_privilege_status = index2.data()

        self.privilege_window = PrivilegesWindow(current_privilege, current_privilege_status)
        self.privilege_window.show()


class IntegrityWindow(QMainWindow):
    def __init__(self, current_integrity):
        super(IntegrityWindow, self).__init__()
        self.current_integrity = current_integrity
        self.setupUi()

    def setupUi(self):
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(self)

        self.integrity_chosen = QComboBox(self)
        self.integrity_chosen.addItems(INTEGRITY_LEVELS)
        self.integrity_chosen.setCurrentText(self.current_integrity)
        self.integrity_chosen.move(50, 20)

        button = QPushButton("Change", self)
        button.move(50, 65)
        button.clicked.connect(self.change_integrity_level)

    def change_integrity_level(self):
        new_integrity_level = self.integrity_chosen.currentText()
        if new_integrity_level == self.current_integrity:
            self.showDialog({
                'icon': QMessageBox.Information,
                'main_text': 'There were no changes. First change the setting and try again.',
                'title_text': 'Information: There were no changes'
            })
        elif INTEGRITY_LEVELS.index(new_integrity_level) >= INTEGRITY_LEVELS.index(self.current_integrity):
            self.showDialog({
                'icon': QMessageBox.Critical,
                'main_text': 'Unable to increase integrity level. Try to choose another integrity level !',
                'title_text': 'Error: Unable to increase integrity level'
            })
        else:
            db = DataBase()
            db.change_integrity_level(db.json_array[db.current_index]['PID'], new_integrity_level)

            self.showDialog({
                'icon': QMessageBox.Information,
                'main_text': 'The data has been successfully changed. Check the integrity level of this process !',
                'title_text': 'Ok: The data has been successfully changed'
            })
            self.close()

    def showDialog(self, params):
        self.integity_msgBox = QMessageBox()
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.integity_msgBox.setWindowIcon(icon)
        self.integity_msgBox.setIcon(params['icon'])
        self.integity_msgBox.setText(params["main_text"])
        self.integity_msgBox.setWindowTitle(params["title_text"])
        self.integity_msgBox.setStandardButtons(QMessageBox.Ok)
        self.integity_msgBox.show()


class IntegrityTableView(QtWidgets.QTableView):

    def mouseDoubleClickEvent(self, event):
        index = self.currentIndex().siblingAtColumn(0)
        current_integrity = index.data()

        if current_integrity in INCORRECT_INTEGRITY_LEVELS:
            self.showDialog()
        else:
            self.integrity_window = IntegrityWindow(current_integrity)
            self.integrity_window.show()

    def showDialog(self):
        self.msgBox = QMessageBox()
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.msgBox.setWindowIcon(icon)
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setText("Changing the integrity level is not possible due to an incorrect value or a low integrity level")
        self.msgBox.setWindowTitle("Warning: Changing is not possible!")
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.show()


class AdditionalWindow(QMainWindow):
    def __init__(self, name_process):
        super(AdditionalWindow, self).__init__()
        self.name_process = name_process
        self.db = DataBase()
        self.create_menu()
        self.setupUi()

    def create_menu(self):
        self.refresh_action = QAction(QIcon(f'{PATH_MEDIA_FILES}/refresh.png'), '&Refresh', self)
        self.refresh_action.setShortcut('Ctrl+U')
        self.refresh_action.triggered.connect(self.refresh_additional_table)

        self.menu_bar = self.menuBar()
        self.menu_bar.addAction(self.refresh_action)

    def setupUi(self):
        self.setWindowTitle(self.name_process)
        width = 700
        height = 800
        self.setGeometry(300, 200, width, height)
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
        self.create_table_with_integrity()
        self.create_table_with_dlls()
        self.create_table_with_privileges()

        self.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(self)

    def refresh_additional_table(self):
        self.db.update_process_information()
        self.setupUi()

    def create_table_with_additional_info(self):
        self.additional_table = QtWidgets.QTableView(self.verticalLayoutWidget)

        self.additional_table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        additional_info = serialize_additional_info(self.db.json_array, self.db.current_index)
        count_process = len(additional_info)
        data_table = pd.DataFrame(additional_info, columns=COLUMNS_ADDITIONAL_TABLE,
                                  index=[str(i) for i in range(1, count_process + 1)])

        self.additional_table.setMinimumHeight(290)

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

        dlls_info = serialize_list_dlls(self.db.json_array, self.db.current_index)
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

    def create_table_with_integrity(self):
        self.integrity_table = IntegrityTableView()

        self.integrity_table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        integrity_info = serialize_integrity_level(self.db.json_array, self.db.current_index)
        count_integrity = 1
        data_table = pd.DataFrame(integrity_info, columns=COLUMN_INTEGRITY,
                                  index=[str("") for i in range(1, count_integrity + 1)])

        self.integrity_table.setFixedHeight(60)

        header_h = self.integrity_table.horizontalHeader()
        header_h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        header_v = self.integrity_table.verticalHeader()
        header_v.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        model_table = TableModel(data_table)
        self.integrity_table.setModel(model_table)

        self.integrity_table.setObjectName("integrity_table")
        self.verticalLayout.addWidget(self.integrity_table)

    def create_table_with_privileges(self):
        self.privileges_table = PrivilegesTableView()

        self.privileges_table.setStyleSheet(
            """
            background-color: #ffdea1;
            """
        )

        privileges_info = serialize_list_privileges(self.db.json_array, self.db.current_index)
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
        db = DataBase()
        db.set_index(index.row())

        self.additional_window = AdditionalWindow(name_process)
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


class OwnerFileWindow(QMainWindow):
    def __init__(self):
        super(OwnerFileWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(self)

        self.path_file_owner = QtWidgets.QFileDialog.getOpenFileName()[0]
        if len(self.path_file_owner) > 0:
            self.owner_chosen = QComboBox(self)
            self.owner_chosen.addItems(OWNER_CHOSEN)
            self.owner_chosen.move(50, 20)

            button = QPushButton("Change", self)
            button.move(50, 65)
            button.clicked.connect(self.change_owner_file)
        else:
            button = QPushButton("Exit", self)
            button.move(50, 65)
            button.clicked.connect(self.exit_window)

    def exit_window(self):
        self.close()

    def change_owner_file(self):
        new_owner_file = self.owner_chosen.currentText()
        db = DataBase()
        db.change_owner_file(self.path_file_owner, new_owner_file)

        self.showDialog({
            'icon': QMessageBox.Information,
            'main_text': 'The data has been successfully changed. Check the owner of this file !',
            'title_text': 'Ok: The data has been successfully changed'
        })
        self.close()

    def showDialog(self, params):
        self.integity_msgBox = QMessageBox()
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.integity_msgBox.setWindowIcon(icon)
        self.integity_msgBox.setIcon(params['icon'])
        self.integity_msgBox.setText(params["main_text"])
        self.integity_msgBox.setWindowTitle(params["title_text"])
        self.integity_msgBox.setStandardButtons(QMessageBox.Ok)
        self.integity_msgBox.show()


class IntegrityFileWindow(QMainWindow):
    def __init__(self):
        super(IntegrityFileWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(self)

        self.path_file = QtWidgets.QFileDialog.getOpenFileName()[0]
        if len(self.path_file) > 0:
            self.integrity_chosen = QComboBox(self)
            self.integrity_chosen.addItems(INTEGRITY_LEVELS)
            self.integrity_chosen.move(50, 20)

            button = QPushButton("Change", self)
            button.move(50, 65)
            button.clicked.connect(self.change_integrity_level)
        else:
            button = QPushButton("Exit", self)
            button.move(50, 65)
            button.clicked.connect(self.exit_window)

    def exit_window(self):
        self.close()

    def change_integrity_level(self):
        new_integrity_level = self.integrity_chosen.currentText()
        db = DataBase()
        db.change_integrity_level_file(self.path_file, new_integrity_level)

        self.showDialog({
            'icon': QMessageBox.Information,
            'main_text': 'The data has been successfully changed. Check the integrity level of this file !',
            'title_text': 'Ok: The data has been successfully changed'
        })
        self.close()

    def showDialog(self, params):
        self.integity_msgBox = QMessageBox()
        icon = QIcon(f'{PATH_MEDIA_FILES}/info.png')
        self.integity_msgBox.setWindowIcon(icon)
        self.integity_msgBox.setIcon(params['icon'])
        self.integity_msgBox.setText(params["main_text"])
        self.integity_msgBox.setWindowTitle(params["title_text"])
        self.integity_msgBox.setStandardButtons(QMessageBox.Ok)
        self.integity_msgBox.show()


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

        file_integrity_action = QAction('&Сhange File Integrity', self)
        file_integrity_action.setShortcut('Ctrl+I')
        file_integrity_action.triggered.connect(self.change_file_integrity)

        menu_bar = self.menuBar()
        menu_bar.addAction(refresh_action)

        action_menu = menu_bar.addMenu("&Action")
        action_menu.addAction(file_owner_action)
        action_menu.addAction(file_integrity_action)

    def refresh_table(self):
        self.db.update_process_information()
        self.create_table()

    def change_file_owner(self):
        self.owner_file_window = OwnerFileWindow()
        self.owner_file_window.show()

    def change_file_integrity(self):
        self.integrity_file_window = IntegrityFileWindow()
        self.integrity_file_window.show()


def application():
    app = QApplication(sys.argv)

    window = Window()
    window.db.update_process_information()
    window.create_table()
    window.create_menu_bar()

    window.show()
    sys.exit(app.exec_())
