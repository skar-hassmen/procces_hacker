from constants import PATH_CONSOLE_PROGRAM, PATH_FILE_JSON
import subprocess
import json


class DataBase:
    def __init__(self):
        self.json_array = None

    def read_json_file(self):
        f_json = open(PATH_FILE_JSON, "r", encoding='utf-8')
        data = json.load(f_json)
        f_json.close()
        return data

    def update_process_information(self):
        subprocess.Popen(PATH_CONSOLE_PROGRAM)
        self.json_array = self.read_json_file()
