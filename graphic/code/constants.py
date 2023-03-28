PATH_FILE_JSON = "./../../data.json"

PATH_CONSOLE_PROGRAM = "./../../console/code/x64/Debug/code.exe"

COLUMNS = ['Name', 'PID', 'PID parent', 'SID', 'Owner User', 'Type', 'DEP', 'Execution\nenvironment',
           'Description', 'Name\nparent']

NAMES_FOR_SERIALIZER_TABLE = [
        'name_process',
        'PID',
        'PID_parent',
        'SID',
        'name_owner_user',
        'type_process',
        'DEP',
        'execution_environment',
        'description_process',
        'parent_name'
    ]

PATH_MEDIA_FILES = "./../media"

NAMES_ADDITIONAL_INFO = [
        'path_exe',
        'ASLR_EnableBottomUpRandomization',
        'ASLR_EnableForceRelocateImages',
        'ASLR_EnableHighEntropy',
        'list_dll',
        'privileges'
]
