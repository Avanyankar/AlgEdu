#pragma once
#include <string>
#include <unordered_set>
#include "lexer.h"
#include "token.h"
#include "tokenType.h"
#include "baseStatement.h"

class Parser {
 private:
    Lexer* lexer;
    Token curToken;
    Token peekToken;
    explicit Parser(std::string source);
    static Parser* instance;
    std::vector<BaseStatement> enabledStatements;
 public:
    static Parser* getInstance(std::string source);
    bool checkToken(TokenType kind);
    void match(TokenType kind);
    void nextToken();
    bool isComparisonOperator();
    void abort(const std::string& message);
    void program();
    void statement();
    void nl();
};
