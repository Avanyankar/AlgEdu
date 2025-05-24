#pragma once
#include "baseStatement.h"

class Declaration :
    public BaseStatement
{
    bool match(const std::vector<Token>& statement) const override;
    void instructions(std::vector<Token>& statement) const override;
};
