from constants import PATH_CONSOLE_PROGRAM, PATH_FILE_JSON, UPDATE_FLAG, SET_INTEGRITY_FLAG, SET_PRIVILEGE_FLAG, \
    STATUS_PRIVILEGES, SET_INTEGRITY_FILE_FLAG, SET_FILE_OWNER_FLAG
import subprocess
import json


class DataBase:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataBase, cls).__new__(cls)
        return cls.instance

    def set_index(self, index):
        self.current_index = index

    def read_json_file(self):
        f_json = open(PATH_FILE_JSON, "r", encoding='utf-8')
        data = json.load(f_json)
        f_json.close()
        return data

    def update_process_information(self):
        subprocess.Popen(f'{PATH_CONSOLE_PROGRAM} {UPDATE_FLAG}')
        self.json_array = self.read_json_file()

    def change_integrity_level(self, pid, level):
        subprocess.Popen(f'{PATH_CONSOLE_PROGRAM} {SET_INTEGRITY_FLAG} {pid} {level}')

    def change_status_privilege(self, pid, name_privilege, status_privilege):
        subprocess.Popen(f'{PATH_CONSOLE_PROGRAM} {SET_PRIVILEGE_FLAG} {pid} {name_privilege} {STATUS_PRIVILEGES[status_privilege]}')

    def change_integrity_level_file(self, path, level):
        subprocess.Popen(f'{PATH_CONSOLE_PROGRAM} {SET_INTEGRITY_FILE_FLAG} {path} {level}')

    def change_owner_file(self, path, owner):
        subprocess.Popen(f'{PATH_CONSOLE_PROGRAM} {SET_FILE_OWNER_FLAG} {path} {owner}')

