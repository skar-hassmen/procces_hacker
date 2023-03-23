#include "JSONoutput.h"
#include <vector>
#include <windows.h>
void JSONoutput::printVal(std::wstring val)
{
	fprintf(fn, "\"%ws\"", val.c_str());
}
void JSONoutput::printVal(std::vector<std::wstring> val)
{
	fprintf(fn, "[");
	for (int j = 0; j < val.size(); ++j) {
		printVal(val.at(j));
		if (j != val.size() - 1)
			fprintf(fn, ", ");
	}
	fprintf(fn, "]");
}
void JSONoutput::printVal(std::vector<std::pair<std::wstring, DWORD>> val) {
	fprintf(fn, "[");
	for (int j = 0; j < val.size(); ++j) {
		fprintf(fn, "[");
		printVal(val.at(j).first);
		fprintf(fn, " , ");
		printVal(val.at(j).second);
		fprintf(fn, "]");
		if (j != val.size() - 1)
			fprintf(fn, ", ");
	}
	fprintf(fn, "]");
}
void JSONoutput::openFile(const char* filename)
{
	setlocale(0, "Rus");

	if (fn) fclose(fn);
	fopen_s(&fn, filename, "w");
}
void JSONoutput::closeFile()
{
	if (obj_opened) fprintf(fn, "}\n");
	fclose(fn);
}
void JSONoutput::createNewObject(const char* obj)
{

	if (obj_opened) {
		fprintf(fn, "}\n");
	}
	obj_opened = true;
	fprintf(fn, "{\n");
}

