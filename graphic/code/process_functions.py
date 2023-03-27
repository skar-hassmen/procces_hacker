import subprocess
from constants import PATH_CONSOLE_PROGRAM
from json_functions import read_json_file


def update_process_information():
    subprocess.Popen(PATH_CONSOLE_PROGRAM)
    return read_json_file()