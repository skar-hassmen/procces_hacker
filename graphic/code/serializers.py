from constants import NAMES_FOR_SERIALIZER_TABLE, NAMES_ADDITIONAL_INFO, NAMES_ADDITIONAL_INFO_ROWS


def serialize_data_for_table(json_file):
    data_process = []
    bool_to_string = ['Yes', 'No']
    for js in json_file:
        one_process = []
        for name in NAMES_FOR_SERIALIZER_TABLE:
            if name == 'DEP':
                one_process.append(bool_to_string[int(js[name])])
            elif len(js[name]) > 0:
                one_process.append(js[name])
            else:
                one_process.append("No data")

        data_process.append(one_process)

    return data_process


def serialize_additional_info(json_file, index):
    bool_to_string = ['Yes', 'No']
    one_process = []
    for ind, name in enumerate(NAMES_ADDITIONAL_INFO):
        if "ASL" in name:
            one_process.append([NAMES_ADDITIONAL_INFO_ROWS[ind], bool_to_string[int(json_file[index][name])]])
        elif len(json_file[index][name]) > 0:
            one_process.append([NAMES_ADDITIONAL_INFO_ROWS[ind], json_file[index][name]])
        else:
            one_process.append([NAMES_ADDITIONAL_INFO_ROWS[ind], "No data"])

    return one_process


def serialize_list_dlls(json_file, index):
    list_dlls = []
    if len(json_file[index]['list_dll']) > 0:
        for elem in json_file[index]['list_dll']:
            list_dlls.append([elem])
    else:
        list_dlls.append(["No data"])

    return list_dlls


def serialize_list_privileges(json_file, index):
    list_privileges = []
    if len(json_file[index]['privileges']) > 0:
        for elem in json_file[index]['privileges']:
            list_privileges.append([elem, 'None'])
    else:
        list_privileges.append(["No data", "No data"])

    return list_privileges