#include <nlohmann/json.hpp>


nlohmann::json Serializer(std::vector<std::string>, std::vector<std::string>);
std::vector<nlohmann::json> Test();
void WriteDataToJsonFile();


std::string PATH_JSON = "D:\\github_mbks2\\mbks2\\data.json";