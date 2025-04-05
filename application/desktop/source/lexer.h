#pragma once

class Token
{
private:
    std::string source;
    TokenType type;
public:
    Token(){}
    Token(std::string source, TokenType type){}
    Token& setType(TokenType type){}
    TokenType getType(){}
    Token& setSource(std::string source){}
    std::string getSource(){}
};