#pragma once
#include <vector>
#include <stdexcept>
#include <unordered_map>
#include "tokenType.h"
#include "token.h"
#include "integer.h"

class BaseStatement
{
 public:
     static std::unordered_map<std::string, Integer> variables;
     virtual void instructions(std::vector<Token>& statement) = 0;
     virtual void instructions(std::vector<Token>& statement) const = 0;
     virtual bool match(std::vector<Token>& statement) const = 0;
     virtual ~BaseStatement() = default;
};
