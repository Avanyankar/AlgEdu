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
     static std::unordered_map<std::string, Integer> integers;
     virtual void instructions(std::vector<Token>& statement) const = 0;
     virtual bool match(const std::vector<Token>& statement) const = 0;
     bool match_condition(const std::vector<Token>& statement, size_t* i) const;
     bool match_not_condition(const std::vector<Token>& statement, size_t* i) const;
     bool match_and_condition(const std::vector<Token>& statement, size_t* i) const;
     bool match_comparison(const std::vector<Token>& statement, size_t* i) const;
     bool match_expression(const std::vector<Token>& statement, size_t* i) const;
     bool match_term(const std::vector<Token>& statement, size_t* i) const;
     bool match_unary(const std::vector<Token>& statement, size_t* i) const;
     bool match_primary(const std::vector<Token>& statement, size_t* i) const;
     int calculate_expression(const std::vector<Token>& statement, size_t* i) const;
     virtual ~BaseStatement() = default;
};
