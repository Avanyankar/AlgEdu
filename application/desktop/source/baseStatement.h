#pragma once
#include "tokenType.h"
#include "token.h"
#include <vector>
#include <stdexcept>
#include <unordered_map>
#include "baseVariable.h"

class BaseStatement
{
public:
    virtual void instructions(std::vector<Token>& statement) = 0;
    virtual void instructions(std::vector<Token>& statement) const = 0;
    virtual bool match(std::vector<Token>& statement) const = 0;
    virtual ~BaseStatement() = default;
};
