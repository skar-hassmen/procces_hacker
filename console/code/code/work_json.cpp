#include <iostream>
#include <nlohmann/json.hpp>
#include <ostream>
#include <fstream>
#include <vector>
#include <string>
#include "work_json.hpp"


struct Proccess {
    std::string name_proccess;
    std::string description_proccess;
    std::string PID;
    std::string path_exe;
    std::string name_parent;
    std::string PID_parent;
    std::string name_owner_user;
    std::string SID;
    std::string type_proccess;
    std::string execution_environment;
    std::string DEP_or_ASLR;
    std::vector<std::string> list_dll;
    std::string additional_info;
};


nlohmann::json Serializer(const Proccess &p) {
    nlohmann::json js{};
    js["name_proccess"] = p.name_proccess;
    js["description_proccess"] = p.description_proccess;
    js["PID"] = p.PID;
    js["path_exe"] = p.path_exe;
    js["name_parent"] = p.name_parent;
    js["PID_parent"] = p.PID_parent;
    js["name_owner_user"] = p.name_owner_user;
    js["SID"] = p.SID;
    js["type_proccess"] = p.type_proccess;
    js["execution_environment"] = p.execution_environment;
    js["DEP_or_ASLR"] = p.DEP_or_ASLR;
    js["list_DLL"] = p.list_dll;
    js["additional_info"] = p.additional_info;
    return js;
}


std::vector<nlohmann::json> Test() {
    Proccess proc;
    std::vector<nlohmann::json> vectorOfJson;

    proc.name_proccess = "name_proccess1";
    proc.description_proccess = "description_proccess1";
    proc.PID = "PID1";
    proc.path_exe = "path_exe1";
    proc.name_parent = "name_parent1";
    proc.PID_parent = "PID_parent1";
    proc.name_owner_user = "name_owner_user1";
    proc.SID = "SID1";
    proc.type_proccess = "type_proccess1";
    proc.execution_environment = "execution_environment1";
    proc.DEP_or_ASLR = "DEP_or_ASLR1";
    proc.list_dll = { "DLL1", "DLL2", "DLL3" };
    proc.additional_info = "additional_info1";

    vectorOfJson.push_back(Serializer(proc));

    proc.name_proccess = "name_proccess2";
    proc.description_proccess = "description_proccess2";
    proc.PID = "PID2";
    proc.path_exe = "path_exe2";
    proc.name_parent = "name_parent2";
    proc.PID_parent = "PID_parent2";
    proc.name_owner_user = "name_owner_user2";
    proc.SID = "SID2";
    proc.type_proccess = "type_proccess2";
    proc.execution_environment = "execution_environment2";
    proc.DEP_or_ASLR = "DEP_or_ASLR2";
    proc.list_dll = { "DLL12", "DLL22", "DLL32" };
    proc.additional_info = "additional_info2";

    vectorOfJson.push_back(Serializer(proc));

    return vectorOfJson;
}

void WriteDataToJsonFile(std::vector<nlohmann::json> vectorOfJson) {
    std::ofstream file(PATH_JSON, std::ios_base::out | std::ios_base::trunc);

    if (!file.is_open()) {
        std::cout << "Error Open Json File!\n";
        return;
    }

    file << vectorOfJson;
    file.close();
}


int main(void) {
    std::vector<nlohmann::json> vectorOfJson = Test();
    WriteDataToJsonFile(vectorOfJson);
    return 0;
}