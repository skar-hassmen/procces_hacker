import json
import os
import subprocess
import constants


def read_json_file():
    f_json = open(constants.PATH_FILE_JSON, "r")
    data = json.load(f_json)
    f_json.close()
    return data


def print_menu():
    print(
        "Menu",
        "1. Update process information",
        "2. Exit program",
        sep="\n"
    )


def update_process_information():
    subprocess.Popen(constants.PATH_CONSOLE_PROGRAM)
    js = read_json_file()
    print(js)


def operation_selection(number):
    if number == 1:
        update_process_information()
    elif number == 2:
        exit(1)


def main():
    while True:
        print_menu()
        number = int(input("Input number operations: "))
        operation_selection(number)


if __name__ == '__main__':
    main()
