#define _CRT_SECURE_NO_WARNINGS
#include <Windows.h>
#include <winternl.h>
#include <iostream>
#include <Tlhelp32.h>
#include <psapi.h>
#include <aclapi.h>
#include <vector>
#include <string>
#include <sddl.h>
#include <cstdlib>
#include <locale.h>
#include "JSONoutput.h"


#pragma comment(lib,"ntdll.lib")
#pragma comment(lib,"Version.lib")

using namespace std;


pair<wstring, wstring> checkSIDAndUsername(HANDLE hProcess) {
    wstring sid;
    wstring usrname;
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
void getProcessName(DWORD pid, WCHAR* fname, DWORD sz)
{
    HANDLE h = NULL;
    int e = 0;
    h = OpenProcess
    (
        PROCESS_QUERY_INFORMATION,
        FALSE,
        pid
    );
    if (h)
    {
        GetModuleFileNameEx(h, NULL, fname, sz);
        CloseHandle(h);
    }

}
wstring findDescription(WCHAR* filename)
{
    wstring out;
    int dwLen = GetFileVersionInfoSize(filename, NULL);
    if (!dwLen)
        return out;

    auto* sKey = new BYTE[dwLen];
    unique_ptr<BYTE[]> skey_automatic_cleanup(sKey);
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
wstring checkIntegrityLevel(HANDLE hProcess) {
    wstring integrity;
    HANDLE hProcessToken;
    if (OpenProcessToken(hProcess, TOKEN_QUERY, &hProcessToken)) {
        DWORD data_length = 0;
        if (!GetTokenInformation(hProcessToken, TokenIntegrityLevel, NULL, 0, &data_length)) {
            TOKEN_MANDATORY_LABEL* data = (TOKEN_MANDATORY_LABEL*)GlobalAlloc(GPTR, data_length);
            if (GetTokenInformation(hProcessToken, TokenIntegrityLevel, data, data_length, &data_length)) {
                SID* sid = static_cast<SID*>(data->Label.Sid);
                DWORD rid = sid->SubAuthority[0];

                switch (rid)
                {
                case SECURITY_MANDATORY_LOW_RID:
                {
                    integrity += L"LOW_INTEGRITY";
                    break;
                }
                case SECURITY_MANDATORY_MEDIUM_RID:
                {
                    integrity += L"MEDIUM_INTEGRITY";
                    break;
                }
                case SECURITY_MANDATORY_HIGH_RID:
                {
                    integrity += L"HIGH_INTEGRITY";
                    break;
                }
                case SECURITY_MANDATORY_SYSTEM_RID:
                {
                    integrity += L"SYSTEM_INTEGRITY";
                    break;
                }
                case SECURITY_MANDATORY_UNTRUSTED_RID:
                {
                    integrity += L"UNTRUSTED_INTEGRITY";
                    break;
                }
                default:
                {
                    integrity += L"UNKNOWN";
                    break;
                }
                }


            }
        }


    }

    return integrity;
}
vector<pair<wstring, DWORD>> CheckPrivilege(HANDLE hProcess)
{
    LUID luid;
    vector<pair<wstring, DWORD>> privileges;
    PRIVILEGE_SET privs;
    HANDLE hProcessToken;
    if (OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hProcessToken)) {
        DWORD data_length = 0;
        if (!GetTokenInformation(hProcessToken, TokenPrivileges, NULL, 0, &data_length)) {
            TOKEN_PRIVILEGES* data = (TOKEN_PRIVILEGES*)GlobalAlloc(GPTR, data_length);
            if (GetTokenInformation(hProcessToken, TokenPrivileges, data, data_length, &data_length)) {
                for (int i = 0; i < data->PrivilegeCount; ++i) {
                    wstring priv;
                    WCHAR pname[128];
                    DWORD dwSize = 128;
                    LookupPrivilegeName(NULL, &data->Privileges[i].Luid, pname, &dwSize);
                    priv += pname;
                    privileges.push_back(make_pair(priv, data->Privileges[i].Attributes));

                }



            }

        }


    }

    return privileges;
}
int update() {
    JSONoutput jso;
    jso.openFile("out.json");

    PROCESSENTRY32 peProcessEntry;
    DWORD dwTemp;
    HANDLE CONST hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hSnapshot) {
        return -1;
    }


    peProcessEntry.dwSize = sizeof(PROCESSENTRY32);
    Process32First(hSnapshot, &peProcessEntry);
    do {
        char objName[64];
        _itoa(peProcessEntry.th32ProcessID, objName, 10);
        jso.createNewObject(objName);
        jso.write("PID", peProcessEntry.th32ProcessID);
        jso.write("NAME", peProcessEntry.szExeFile);
        HANDLE processHandle = OpenProcess(MAXIMUM_ALLOWED, FALSE, peProcessEntry.th32ProcessID);
        BOOL sysWOW = FALSE;
        WCHAR procPATH[512];

        IsWow64Process(processHandle, &sysWOW);
        DWORD num = GetModuleFileNameEx(processHandle, NULL, procPATH, 512);
        wstring wpath;
        for (int i = 0; i < num; ++i)wpath += procPATH[i];


        wstring description = findDescription(procPATH);
        BOOL res = FALSE;
        jso.write("PATH", wpath);

        jso.write("x64", sysWOW);

        jso.write("DESCRIPTION", (description.size()) ? description : L"(null)");

        WCHAR parentName[256];
        getProcessName(peProcessEntry.th32ParentProcessID, parentName, 256);

        pair<wstring, wstring> SIDandNAME = checkSIDAndUsername(processHandle);
        wstring integrity = checkIntegrityLevel(processHandle);

        jso.write("USER_SID", SIDandNAME.first);
        jso.write("USERNAME", SIDandNAME.second);
        jso.write("INTEGRITY", integrity);

        vector<pair<wstring, DWORD>> privileges = CheckPrivilege(processHandle);


        jso.write("PRIVILEGES", privileges);




        PROCESS_MITIGATION_DEP_POLICY dep = { 0 };
        PROCESS_MITIGATION_ASLR_POLICY aslr = { 0 };
        GetProcessMitigationPolicy(processHandle, ProcessDEPPolicy, &dep, sizeof(dep));
        GetProcessMitigationPolicy(processHandle, ProcessASLRPolicy, &aslr, sizeof(aslr));

        jso.write("USING_DEP", (BOOL)dep.Enable);
        jso.write("USING_ASLR(EnableBottomUpRandomization)", (BOOL)aslr.EnableBottomUpRandomization);
        jso.write("USING_ASLR(EnableForceRelocateImages)", (BOOL)aslr.EnableForceRelocateImages);
        jso.write("USING_ASLR(EnableHighEntropy)", (BOOL)aslr.EnableHighEntropy);

        BOOL isDotNet = FALSE;
        vector<wstring> dlls;
        MODULEENTRY32 meModuleEntry;
        DWORD dwTemp;
        HANDLE CONST mSnapshot = CreateToolhelp32Snapshot(
            TH32CS_SNAPMODULE, peProcessEntry.th32ProcessID);
        if (INVALID_HANDLE_VALUE != mSnapshot) {
            meModuleEntry.dwSize = sizeof(MODULEENTRY32);
            Module32First(mSnapshot, &meModuleEntry);
            do {
                if (wcscmp(meModuleEntry.szModule, L"mscoree.dll") == 0) isDotNet = TRUE;
                wstring dll;
                for (int i = 0; meModuleEntry.szModule[i] != 0x00; ++i) dll += meModuleEntry.szModule[i];
                dlls.push_back(dll);

            } while (Module32Next(mSnapshot, &meModuleEntry));

            CloseHandle(mSnapshot);

        }


        jso.write("DLLS", dlls);

        jso.write("USE_DOTNET", isDotNet);

    } while (Process32Next(hSnapshot, &peProcessEntry));
    jso.closeFile();
    CloseHandle(hSnapshot);

    return 0;
}
int main(int argc, char* argv[]) {
    setlocale(LC_ALL, "Russian");
    update();
    return 0;
}


