PATH_FILE_JSON = "./../../data.json"

PATH_CONSOLE_PROGRAM = "./../../console/code/x64/Debug/code.exe"

UPDATE_FLAG = "--update"
SET_INTEGRITY_FLAG = "--setIntegrity"
SET_FILE_OWNER_FLAG = "--setFileOwner"
PRINT_FILE_OWNER = "--printFileOwner"
SET_PRIVILEGE_FLAG = "--setPrivilege "

COLUMNS = ['Name', 'PID', 'PID parent', 'Owner User', 'Type', 'DEP', 'Execution\nenvironment',
           'Description']

NAMES_FOR_SERIALIZER_TABLE = [
        'name_process',
        'PID',
        'PID_parent',
        'name_owner_user',
        'type_process',
        'DEP',
        'execution_environment',
        'description_process',
    ]

PATH_MEDIA_FILES = "./../media"

NAMES_ADDITIONAL_INFO = [
        'path_exe',
        'SID',
        'parent_name',
        'ASLR_EnableBottomUpRandomization',
        'ASLR_EnableForceRelocateImages',
        'ASLR_EnableHighEntropy',
]

NAMES_ADDITIONAL_INFO_ROWS = [
        'Path exe:',
        'SID:',
        'Parent name:',
        'ASLR\nEnableBottomUpRandomization:',
        'ASLR\nEnableForceRelocateImages:',
        'ASLR\nEnableHighEntropy:'
]

COLUMNS_ADDITIONAL_TABLE = [
        'Name',
        'Value'
]

COLUMN_DLL = ['List Dll']

COLUMN_PRIVILEGES = [
        'Name Privilege',
        'On/Off'
]

COLUMN_INTEGRITY = [
        "Level Integrity"
]

INTEGRITY_LEVELS = [
        'LOW',
        'MEDIUM',
        'HIGH'
]

INCORRECT_INTEGRITY_LEVELS = [
        'SYSTEM',
        'UNTRUSTED',
        'UNKNOWN',
        'LOW',
        'No data'
]
