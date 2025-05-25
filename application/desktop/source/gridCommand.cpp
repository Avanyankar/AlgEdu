#include "gridCommand.h"

GridCommand::GridCommand() : 
	type(CMD_NONE), x(0), y(0), steps(1)
{
}

GridCommand::GridCommand(CommandType t, int s) :
	type(t), x(0), y(0), steps(s)
{
}

GridCommand::GridCommand(CommandType t, int _x, int _y) :
	type(t), x(_x), y(_y), steps(1)
{
}
