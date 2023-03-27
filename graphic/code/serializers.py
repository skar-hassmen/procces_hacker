from constants import NAMES_FOR_SERIALIZER_TABLE


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
