#pragma once
#include "tokentype.h"
#include <string>

class Token
{
private:
    std::string source;
    TokenType type;
public:
    Token();
    Token(std::string source, TokenType type);
    void setType(TokenType type);
    TokenType getType();
    TokenType getType() const;
    void setSource(std::string source);
    std::string getSource();
    std::string getSource() const;
};