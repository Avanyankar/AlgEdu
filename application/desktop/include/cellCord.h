#pragma once

class CellCoord
{
 public:
     int x, y;
     CellCoord();
     CellCoord(int _x, int _y);
     bool operator==(const CellCoord& other) const;
     bool operator<(const CellCoord& other) const;
};
