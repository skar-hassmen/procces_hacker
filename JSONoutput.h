#include <iostream>
#include <vector>
#include <windows.h>
class JSONoutput
{
private:
	FILE* fn = 0x00;
	bool obj_opened = false;
	void printVal(std::wstring val);
	void printVal(std::vector<std::wstring> val);
	void printVal(std::vector<std::pair<std::wstring, DWORD>> val);
	template<typename G>
	void printVal(G val);
public:
	void openFile(const char* filename);
	void closeFile();
	template<typename T>
	void write(const char* obj, T value);
	void createNewObject(const char* obj);
};

template<typename G>
void JSONoutput::printVal(G val)
{
	if (std::is_same<G, DWORD>::value) {
		fprintf(fn, "\"%d\"", val);
	}
	else if (std::is_same<G, wchar_t*>::value) {
		fprintf(fn, "\"%ws\"", val);
	}
	else if (std::is_same<G, char*>::value) {
		fprintf(fn, "\"%s\"", val);
	}
	else if (std::is_same<G, BOOL>::value || std::is_same<G, bool>::value) {
		fprintf(fn, "%s", (val) ? "true" : "false");
	}
}

template<typename T>
inline void JSONoutput::write(const char* obj, T val)
{
	fprintf(fn, " \"%s\": ", obj);
	printVal(val);
	fprintf(fn, "\n");


}

