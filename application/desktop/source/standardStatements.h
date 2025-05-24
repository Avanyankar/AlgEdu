#pragma once
#include <vector>
#include "baseStatement.h"
#include "declaration.h"
#include "assignment.h"

const std::vector<BaseStatement> standardStatements
{
    Declaration(),
    Assignment(),
    /*
    If,
    For,
    While,
    DoWhile
    */
};
