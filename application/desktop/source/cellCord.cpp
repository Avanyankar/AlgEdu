#include "cellCord.h"

CellCoord::CellCoord() :
	x(0), y(0)
{
}

CellCoord::CellCoord(int _x, int _y) :
	x(_x), y(_y)
{
}

bool CellCoord::operator==(const CellCoord& other) const
{
	return x == other.x && y == other.y;
}

bool CellCoord::operator<(const CellCoord& other) const
{
	return (x < other.x) || (x == other.x && y < other.y);
}
