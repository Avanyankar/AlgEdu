#pragma once
#include <vector>
#include "baseStatement.h"
#include "declaration.h"
#include "assignment.h"

BaseStatement* standardStatements[2] = 
{
    new Declaration,
    new Assignment,
    /*
    If,
    For,
    While,
    DoWhile
    */
};
