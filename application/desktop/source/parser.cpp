#include <iostream>
#include <string>
#include <unordered_set>
#include <cstdlib>
#include "lex.h"
#include "emitter.h"
#include "token.h"
#include "tokenType.h"

Parser::Parser(Lexer* lexer, Emitter* emitter)
{
    this->lexer = lexer;
    this->emitter = emitter;
    this->curToken = nullptr;
    this->peekToken = nullptr;
    nextToken();
    nextToken();
 }

bool Parser::checkToken(TokenType kind)
{
    return kind == curToken->kind;
}

bool Parser::checkPeek(TokenType kind)
{
    return kind == peekToken->kind;
}

void Parser::match(TokenType kind)
{
    if (!checkToken(kind))
    {
        abort("Expected " + tokenTypeToString(kind) + ", got " + tokenTypeToString(curToken->kind));
    }
    nextToken();
}

void Parser::nextToken()
{
    delete curToken;
    curToken = peekToken;
    peekToken = lexer->getToken();
}

bool Parser::isComparisonOperator()
{
    return checkToken(TokenType::GT) || checkToken(TokenType::GTEQ) ||
        checkToken(TokenType::LT) || checkToken(TokenType::LTEQ) ||
        checkToken(TokenType::EQEQ) || checkToken(TokenType::NOTEQ);
}

void Parser::abort(const std::string& message)
{
    std::cerr << "Error! " << message << std::endl;
}

void Parser::program()
{
    while (checkToken(TokenType::NEWLINE))
    {
        nextToken();
    }
    while (!checkToken(TokenType::ENDOFFILE))
    {
        statement();
    }
}

void Parser::statement()
{
    ...
    nl();
}

void Parser::comparison()
{
    expression();
    if (isComparisonOperator())
    {
        emitter->emit(...);
        nextToken();
        expression();
    }
    while (isComparisonOperator())
    {
        emitter->emit(...);
        nextToken();
        expression();
    }
}

void Parser::expression()
{
    term();
    while (checkToken(TokenType::PLUS) || checkToken(TokenType::MINUS))
    {
        emitter->emit(...);
        nextToken();
        term();
    }
}

void term()
{
    unary();
    while (checkToken(TokenType::ASTERISK) || checkToken(TokenType::SLASH))
    {
        emitter->emit(...);
        nextToken();
        unary();
    }
}

void Parser::unary()
{
    if (checkToken(TokenType::PLUS) || checkToken(TokenType::MINUS))
    {
        emitter->emit(...);
        nextToken();
    }
    primary();
}

void Parser::primary()
{
    if (checkToken(TokenType::NUMBER))
    {
        emitter->emit(curToken->text);
        nextToken();
    }
    else if (checkToken(TokenType::IDENT))
    {
        if (symbols.find(curToken->text) == symbols.end())
        {
            abort("Referencing variable before assignment: " + curToken->text);
        }
        emitter->emit(...);
        nextToken();
    }
    else
    {
        abort("Unexpected token at " + curToken->text);
    }
}

void Parser::nl()
{
    match(TokenType::NEWLINE);
    while (checkToken(TokenType::NEWLINE))
    {
        nextToken();
    }
}
