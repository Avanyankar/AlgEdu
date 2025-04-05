#pragma once
#include <vector>

class Cell
{
public:
	int x;
	int y;
};

class Field
{
public:
	std::vector<std::vector<Cell>> cells;

	Field(int w = 0, int h = 0) : cells(h, std::vector<Cell>(w)){}

	~Field(){}

	Cell& at(int x, int y){}
};