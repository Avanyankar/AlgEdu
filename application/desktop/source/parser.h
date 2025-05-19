#pragma once
#include <string>
#include <unordered_set>
#include "lexer.h"
#include "token.h"
#include "tokenType.h"

class Parser {
 private:
    Lexer* lexer;
    Token curToken;
    Token peekToken;
    Parser(std::string source);
    static Parser* instance;
 public:
    static Parser* getInstance(std::string source);
    bool checkToken(TokenType kind);
    void match(TokenType kind);
    void nextToken();
    bool isComparisonOperator();
    void abort(const std::string& message);
    void program();
    void statement();
    void comparison();
    void expression();
    void term();
    void unary();
    void primary();
    void nl();
};
