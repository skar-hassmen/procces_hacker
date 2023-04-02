# PATH_FILE_JSON = "./../../data.json"
PATH_FILE_JSON = "./data.json"

# PATH_CONSOLE_PROGRAM = "./../../console/code/x64/Debug/code.exe"
PATH_CONSOLE_PROGRAM = "./code.exe"


UPDATE_FLAG = "--update"
SET_INTEGRITY_FLAG = "--setIntegrity"
SET_FILE_OWNER_FLAG = "--setFileOwner"
SET_PRIVILEGE_FLAG = "--setPrivilege"
SET_INTEGRITY_FILE_FLAG = "--setFileIntegrityLevel"

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

# PATH_MEDIA_FILES = "./../media"
PATH_MEDIA_FILES = "./media"


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
        'Enable/Disable'
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


STATUS_PRIVILEGES = {
        '0': 'Disable',
        '1': 'Enable',
        '2': 'Enable',
        '3': 'Enable',
        'Enable': '1',
        'Disable': '0'
}

PRIVILEGES_CHOSEN = [
        'Enable',
        'Disable'
]

OWNER_CHOSEN = [
        'OWNER',
        'CURRENT'
]

