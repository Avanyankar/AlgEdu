#pragma once
#include "tokenType.h"
#include "token.h"
#include <vector>
#include <stdexcept>
#include <unordered_map>
#include "variable.h"

class Statement
{
public:
    std::vector<std::pair<std::vector<TokenType>, bool>> expected;
    void instructions(const std::vector<Token> statement);
    void instructions(const std::vector<Token> statement) const;
    bool declaration(const std::vector<Token> statement);
    bool declaration(const std::vector<Token> statement) const;
    bool assignment(const std::vector<Token> statement);
    bool assignment(const std::vector<Token> statement) const;
    bool print(const std::vector<Token> statement);
    bool print(const std::vector<Token> statement) const;
    static std::unordered_map<std::string, Integer> integers;
    std::pair<std::vector<TokenType>, bool>& operator[](size_t index);
    const std::pair<std::vector<TokenType>, bool>& operator[](size_t index) const;
    Statement(std::vector<std::pair<std::vector<TokenType>, bool>> _expected);
};
