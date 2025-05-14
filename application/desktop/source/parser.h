#pragma once
#include <string>
#include <unordered_set>
#include "lexer.h"
#include "emitter.h"
#include "token.h"
#include "tokenType.h"
#include "lib.h"

class Parser {
private:
    Lexer* lexer;
    Emitter* emitter;
    std::unordered_set<std::string> symbols;
    std::unordered_set<std::string> labelsDeclared;
    std::unordered_set<std::string> labelsGotoed;
    Token curToken;
    Token peekToken;
    std::vector<Lib> libs;
public:
    Parser(Lexer* lexer, Emitter* emitter);
    bool checkToken(TokenType kind);
    bool checkPeek(TokenType kind);
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
