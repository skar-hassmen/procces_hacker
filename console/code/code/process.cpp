#define _CRT_SECURE_NO_WARNINGS
#include <Windows.h>
#include <winternl.h>
#include <Tlhelp32.h>
#include <psapi.h>
#include <aclapi.h>
#include <iostream>
#include <sddl.h>
#include <cstdlib>
#include <nlohmann/json.hpp>
#include <ostream>
#include <fstream>
#include <vector>
#include <string>
#include "process.hpp"

#pragma comment(lib,"ntdll.lib")
#pragma comment(lib,"Version.lib")


std::string utf8_encode(const std::wstring& wstr) {
    if (wstr.empty()) return std::string();
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, &wstr[0], (int)wstr.size(), NULL, 0, NULL, NULL);
    std::string strTo(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, &wstr[0], (int)wstr.size(), &strTo[0], size_needed, NULL, NULL);
    return strTo;

}


void WriteDataToJsonFile(nlohmann::json jsonArray) {
    std::ofstream file(PATH_JSON, std::ios_base::out | std::ios_base::trunc);

    if (!file.is_open()) {
        std::cout << "Error Open Json File!\n";
        return;
    }

    file << jsonArray;
    file.close();
}


std::vector<std::vector<std::string>> CheckPrivilege(HANDLE hProcess) {
    LUID luid;
    std::vector<std::vector<std::string>> privileges;
    PRIVILEGE_SET privs;
    HANDLE hProcessToken;
    if (OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hProcessToken)) {
        DWORD data_length = 0;
        if (!GetTokenInformation(hProcessToken, TokenPrivileges, NULL, 0, &data_length)) {
            TOKEN_PRIVILEGES* data = (TOKEN_PRIVILEGES*)GlobalAlloc(GPTR, data_length);
            if (GetTokenInformation(hProcessToken, TokenPrivileges, data, data_length, &data_length)) {
                for (int i = 0; i < data->PrivilegeCount; ++i) {
                    std::vector<std::string> tmp;
                    std::wstring priv;
                    WCHAR pname[128];
                    DWORD dwSize = 128;
                    LookupPrivilegeName(NULL, &data->Privileges[i].Luid, pname, &dwSize);
                    priv += pname;
                    tmp.push_back(utf8_encode(priv));
                    tmp.push_back(std::to_string(data->Privileges[i].Attributes));
                    privileges.push_back(tmp);
                }
            }
        }
    }

    return privileges;
}


std::pair<std::wstring, std::wstring> checkSIDAndUsername(HANDLE hProcess) {
    std::wstring sid;
    std::wstring usrname;
    HANDLE hProcessToken;
    if (OpenProcessToken(hProcess, TOKEN_QUERY, &hProcessToken)) {
        DWORD data_length = 0;
        if (!GetTokenInformation(hProcessToken, TokenUser, NULL, 0, &data_length)) {
            PTOKEN_USER data = (PTOKEN_USER)GlobalAlloc(GPTR, data_length);
            if (GetTokenInformation(hProcessToken, TokenUser, data, data_length, &data_length)) {
                WCHAR* sidStr = (WCHAR*)malloc(128 * sizeof(WCHAR));
                ConvertSidToStringSid(data->User.Sid, &sidStr);
                sid += sidStr;
                WCHAR name[128];
                DWORD name_length = 128;
                WCHAR domain[128];
                DWORD domain_length = 128;
                SID_NAME_USE type;
                if (LookupAccountSid(NULL, data->User.Sid, &name[0], &name_length, &domain[0], &domain_length, &type)) {
                    usrname += name;
                    usrname += L"/";
                    usrname += domain;
                }
            }
        }
    }
    return make_pair(sid, usrname);
}


std::wstring findDescription(WCHAR* filename) {
    std::wstring out;
    int dwLen = GetFileVersionInfoSize(filename, NULL);
    if (!dwLen)
        return out;

    auto* sKey = new BYTE[dwLen];
    std::unique_ptr<BYTE[]> skey_automatic_cleanup(sKey);
    if (!GetFileVersionInfo(filename, NULL, dwLen, sKey))
        return out;

    struct LANGANDCODEPAGE {
        WORD wLanguage;
        WORD wCodePage;
    } *lpTranslate;

    UINT cbTranslate = 0;
    if (!VerQueryValue(sKey, L"\\VarFileInfo\\Translation",
        (LPVOID*)&lpTranslate, &cbTranslate))
        return out;

    for (unsigned int i = 0; i < (cbTranslate / sizeof(LANGANDCODEPAGE)); i++)
    {
        WCHAR subblock[256];
        wsprintf(subblock, L"\\StringFileInfo\\%04x%04x\\FileDescription",
            lpTranslate[i].wLanguage, lpTranslate[i].wCodePage);
        WCHAR* description = NULL;
        UINT dwBytes;
        if (VerQueryValue(sKey, subblock, (LPVOID*)&description, &dwBytes)) {
            int k = 0;
            for (; k < dwBytes; ++k) {
                out += description[k];
            }
        }
    }
    return out;
}


int getProcessName(DWORD pid, WCHAR* fname, DWORD sz) {
    HANDLE h = NULL;
    int e = 0;
    h = OpenProcess(
        PROCESS_QUERY_INFORMATION,
        FALSE,
        pid
    );
    if (h) {
        GetModuleFileNameEx(h, NULL, fname, sz);
        CloseHandle(h);
    }
    else {
        return 1;
    }
    return 0;
}


nlohmann::json CollectionOfInformationAboutProcesses(void) {
    PROCESSENTRY32 peProcessEntry;
    DWORD dwTemp;
    HANDLE CONST hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hSnapshot) {
        return std::vector<nlohmann::json> {};
    }

    nlohmann::json jsonArray = nlohmann::json::array();
    int indexArray = 0;

    peProcessEntry.dwSize = sizeof(PROCESSENTRY32);
    Process32First(hSnapshot, &peProcessEntry);
    do {
        char objName[64];

        _itoa(peProcessEntry.th32ProcessID, objName, 10);
        jsonArray[indexArray]["PID"] = std::to_string(peProcessEntry.th32ProcessID);
        jsonArray[indexArray]["name_process"] = utf8_encode(peProcessEntry.szExeFile);

        jsonArray[indexArray]["PID_parent"] = std::to_string(peProcessEntry.th32ParentProcessID);

        HANDLE processHandle = OpenProcess(MAXIMUM_ALLOWED, FALSE, peProcessEntry.th32ProcessID);

        BOOL sysWOW = FALSE;
        WCHAR procPATH[512];

        IsWow64Process(processHandle, &sysWOW);
        DWORD num = GetModuleFileNameEx(processHandle, NULL, procPATH, 512);
        std::wstring wpath;

        for (int i = 0; i < num; ++i)
            wpath += procPATH[i];

        std::wstring description = findDescription(procPATH);
        BOOL res = FALSE;

        jsonArray[indexArray]["path_exe"] = utf8_encode(wpath);
        jsonArray[indexArray]["type_process"] = sysWOW ? "x64" : "x32";
        jsonArray[indexArray]["description_process"] = utf8_encode(description);

        WCHAR parentName[256];
        int statusparentHandle = getProcessName(peProcessEntry.th32ParentProcessID, parentName, 256);
        if (statusparentHandle == 0) {
            jsonArray[indexArray]["parent_name"] = utf8_encode(parentName);
        }
        else {
            jsonArray[indexArray]["parent_name"] = "";
        }

        std::pair<std::wstring, std::wstring> SIDandNAME = checkSIDAndUsername(processHandle);

        jsonArray[indexArray]["SID"] = utf8_encode(SIDandNAME.first);
        jsonArray[indexArray]["name_owner_user"] = utf8_encode(SIDandNAME.second);


        jsonArray[indexArray]["privileges"] = CheckPrivilege(processHandle);

        PROCESS_MITIGATION_DEP_POLICY dep = { 0 };
        PROCESS_MITIGATION_ASLR_POLICY aslr = { 0 };
        GetProcessMitigationPolicy(processHandle, ProcessDEPPolicy, &dep, sizeof(dep));
        GetProcessMitigationPolicy(processHandle, ProcessASLRPolicy, &aslr, sizeof(aslr));

        jsonArray[indexArray]["DEP"] = std::to_string(dep.Enable);
        jsonArray[indexArray]["ASLR_EnableBottomUpRandomization"] = std::to_string(aslr.EnableBottomUpRandomization);
        jsonArray[indexArray]["ASLR_EnableForceRelocateImages"] = std::to_string(aslr.EnableForceRelocateImages);
        jsonArray[indexArray]["ASLR_EnableHighEntropy"] = std::to_string(aslr.EnableHighEntropy);

        BOOL isDotNet = FALSE;
        std::vector<std::string> dlls;
        MODULEENTRY32 meModuleEntry;
        DWORD dwTemp;
        HANDLE CONST mSnapshot = CreateToolhelp32Snapshot(
            TH32CS_SNAPMODULE, peProcessEntry.th32ProcessID);
        if (INVALID_HANDLE_VALUE != mSnapshot) {
            meModuleEntry.dwSize = sizeof(MODULEENTRY32);
            Module32First(mSnapshot, &meModuleEntry);
            int Biba=0;
            do {
                if (wcscmp(meModuleEntry.szModule, L"mscoree.dll") == 0) isDotNet = TRUE;
                std::wstring dll;
                for (int i = 0; meModuleEntry.szModule[i] != 0x00; ++i) dll += meModuleEntry.szModule[i];
                std::string dll_string = utf8_encode(dll);
                if (Biba == 0) 
                {
                    Biba = 1;
                }
                else dlls.push_back(dll_string);

            } while (Module32Next(mSnapshot, &meModuleEntry));

            CloseHandle(mSnapshot);

        }


        jsonArray[indexArray]["list_dll"] = dlls;
        jsonArray[indexArray]["execution_environment"] = isDotNet ? "CLR" : "NATIVE";

        indexArray++;
    } while (Process32Next(hSnapshot, &peProcessEntry));
    CloseHandle(hSnapshot);

    return jsonArray;
}


int setPrivilege(HANDLE processHandle, char* selectedPrivilege, bool isEnabling) {
    HANDLE hToken = NULL;
    if (!OpenProcessToken(processHandle, TOKEN_ADJUST_PRIVILEGES, &hToken))
    {
        return 0;
    }

    LUID luid;
    if (!LookupPrivilegeValueA(NULL, selectedPrivilege, &luid))
    {
        return 0;
    }

    TOKEN_PRIVILEGES pToken;
    pToken.PrivilegeCount = 1;
    pToken.Privileges[0].Luid = luid;
    if (isEnabling)
    {
        pToken.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    }
    else
    {
        pToken.Privileges[0].Attributes = 0;
    }

    if (!AdjustTokenPrivileges(hToken, FALSE, &pToken, sizeof(TOKEN_PRIVILEGES), (PTOKEN_PRIVILEGES)NULL, (PDWORD)NULL))
    {
        return 0;
    }

    if (hToken)
    {
        CloseHandle(hToken);
    }
}
void printFileOwner(const char* path)
{
    LPSTR lpSid = (LPSTR)"UNKNOWN";
    PSID psid = NULL;
    PACL pl = NULL;
    PSECURITY_DESCRIPTOR pDescr;

    if (!GetNamedSecurityInfoA(path, SE_FILE_OBJECT, OWNER_SECURITY_INFORMATION, &psid, NULL, NULL, NULL, &pDescr))
    {

        SID_NAME_USE snu;
        char name[512] = { 0 }, domain[512] = { 0 };
        DWORD nameLen = 512, domainLen = 512;

        if (LookupAccountSidA(NULL, psid, name, &nameLen, domain, &domainLen, &snu))
        {
            ConvertSidToStringSidA(psid, &lpSid);

            printf("Name: %s\n"
                "Domain: %s\n"
                "Sid: %s\n",
                name, domain, lpSid);
        }
    }
    else
    {
        printf("Name: ERROR"
            "Domain: ERROR"
            "Sid: ERROR");
    }

    if (pDescr)
        LocalFree(pDescr);
    if (lpSid)
        LocalFree(lpSid);
}


void setFileOwner(const char* path, const char* user)
{
    char cmd[256] = { 0 };
    strcat(cmd, "takeown /F \"");
    strcat(cmd, path);
    strcat(cmd, "\"");


    if (!strcmp(user, "OWNER")) {
        strcat(cmd, " /A");
        system(cmd);
    }
    else if (!strcmp(user, "CURRENT"))
    {
        system(cmd);
    }
    else
    {
        printf("WRONG ARGS\n");
        return;
    }
}

void setFileIntegrityLevel(const char* path, const char* level)
{
    DWORD dwErr = ERROR_SUCCESS;
    PSECURITY_DESCRIPTOR pSD = NULL;

    PACL pSacl = NULL; // not allocated
    BOOL fSaclPresent = FALSE;
    BOOL fSaclDefaulted = FALSE;
    LPCWSTR sddl;

    if (!strcmp(level, "LOW"))
        sddl = L"S:AI(ML;;NW;;;LW)";
    else if (!strcmp(level, "MEDIUM"))
        sddl = L"S:AI(ML;;NW;;;ME)";
    else if (!strcmp(level, "HIGH"))
        sddl = L"S:AI(ML;;NW;;;HI)";
    else return;

    if (ConvertStringSecurityDescriptorToSecurityDescriptorW(
        sddl, SDDL_REVISION_1, &pSD, NULL))
    {
        if (GetSecurityDescriptorSacl(pSD, &fSaclPresent, &pSacl,
            &fSaclDefaulted))
        {
            // Note that psidOwner, psidGroup, and pDacl are 
            // all NULL and set the new LABEL_SECURITY_INFORMATION
            if (!SetNamedSecurityInfoA((char*)path,
                SE_FILE_OBJECT, LABEL_SECURITY_INFORMATION,
                NULL, NULL, NULL, pSacl))
            {
                printf("SUCCESS\n");
            }
            else
            {
                printf("ACCESS DENIED\n");
            }
        }
        LocalFree(pSD);
    }

}

void setIntegrityLevel(DWORD pid, std::string integrityLevel) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
    if (hProcess == NULL)
    {
        printf("ACCESS DENIED\n");
    }

    WELL_KNOWN_SID_TYPE integritySID;

    if (integrityLevel == "UNTRUSTED")
    {
        integritySID = WinUntrustedLabelSid;

    }
    else if (integrityLevel == "LOW")
    {
        integritySID = WinLowLabelSid;
    }
    else if (integrityLevel == "MEDIUM")
    {
        integritySID = WinMediumLabelSid;
    }
    else if (integrityLevel == "HIGH")
    {
        integritySID = WinHighLabelSid;
    }
    else
    {
        std::cout << "UNKNOWN COMMAND!" << std::endl;
        return;
    }


    TOKEN_MANDATORY_LABEL tml = { { (PSID)alloca(MAX_SID_SIZE), SE_GROUP_INTEGRITY } };

    ULONG cb = MAX_SID_SIZE;

    HANDLE hToken;

    if (!CreateWellKnownSid(integritySID, 0, tml.Label.Sid, &cb) ||
        !OpenProcessToken(hProcess, TOKEN_ADJUST_DEFAULT, &hToken))
    {
        std::cout << GetLastError();
        return;
    }

    ULONG dwError = NOERROR;
    if (!SetTokenInformation(hToken, TokenIntegrityLevel, &tml, sizeof(tml)))
    {
        std::cout << GetLastError();
    }

    CloseHandle(hToken);

}

int main(int argc, char* argv[]) {
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
   // nlohmann::json jsonArray = CollectionOfInformationAboutProcesses();
    //WriteDataToJsonFile(jsonArray);
    if (argc == 2 && std::string(argv[1]) == "--update")
    {
        nlohmann::json jsonArray = CollectionOfInformationAboutProcesses();
        WriteDataToJsonFile(jsonArray);
    }
    if (argc == 4 && std::string(argv[1]) == "--setFileOwner") 
    {
        setFileOwner(argv[2], argv[3]);
    }
    else if (argc == 3 && std::string(argv[1]) == "--printFileOwner")
    {
        printFileOwner(argv[2]);
    }
    else if (argc == 5 && std::string(argv[1]) == "--setPrivilege")
    {
        HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, false, atoi(argv[2]));
        if (hProcess == NULL)
        {
            printf("ACCESS DENIED\n");
            return -1;
        }

        setPrivilege(hProcess, argv[3], argv[4][0] == '1');
        //setPrivilege(argv[3], hProcess, argv[4][0]);

        CloseHandle(hProcess);
    }
    else if (argc == 4 && std::string(argv[1]) == "--setFileIntegrityLevel") {
        setFileIntegrityLevel(argv[2], argv[3]);
    }
    else if (argc == 4 && std::string(argv[1]) == "--setIntegrity")
    {
        setIntegrityLevel(atoi(argv[2]), std::string(argv[3]));
    }
    return 0;
}