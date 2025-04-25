#pragma once

class Lexer
{
private:
    std::string source;
    char curChar;
    int curPos;
    static const std::unordered_map<std::string, TokenType> tokenMap;
public:
    void nextChar();
    void skipWhitespace();
    void skipComment();
    Token getToken();
    void defineToken(Token& token);
    char peek();
    void abort(const std::string& message);
    Lexer(std::string source);
};