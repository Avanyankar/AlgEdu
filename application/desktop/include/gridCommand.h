#pragma once
#include "commandType.h"

class GridCommand
{
 public:
     CommandType type;
     int x;
     int y;
     int steps;
     GridCommand();
     GridCommand(CommandType t, int s = 1);
     GridCommand(CommandType t, int _x, int _y);
};

