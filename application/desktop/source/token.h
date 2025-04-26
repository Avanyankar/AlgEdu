#pragma once

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
    void setSource(std::string source);
    std::string getSource();
};