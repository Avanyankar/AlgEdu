#pragma once
#include <string>
#include <unordered_map>
#include "token.h"
#include "tokenType.h"

class Lexer
{
 private:
    std::string source;
    char curChar;
    int curPos;
    static const std::unordered_map<std::string, TokenType> tokenMap;
    void nextChar();
    void skipWhitespace();
    void skipComment();
    void defineToken(Token& token);
    char peek();
    void abort(const std::string& message);
    explicit Lexer(std::string source);
    static Lexer* instance;
 public:
    Token getToken();
    static Lexer* getInstance(std::string source);
};
