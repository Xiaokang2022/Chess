#pragma once

extern "C" _declspec(dllexport) float search(int data[10][9], int depth, int result[4], bool reverse = false);
extern "C" _declspec(dllexport) void all_operations(int data[10][9], int i, int j, int operation[18][2]);
