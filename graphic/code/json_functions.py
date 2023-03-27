from constants import PATH_FILE_JSON
import json


def read_json_file():
    f_json = open(PATH_FILE_JSON, "r", encoding='utf-8')
    data = json.load(f_json)
    f_json.close()
    return data
