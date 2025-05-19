#include "parser.h"
#include <iostream>

Parser* Parser::getInstance(std::string _source)
{
    if (instance == nullptr)
    {
        instance = new Parser(_source);
    }
    return instance;
}

Parser::Parser(std::string _source)
{
    lexer = Lexer::getInstance(_source);
    curToken;
    peekToken;
    nextToken();
    nextToken();
}

bool Parser::checkToken(TokenType type)
{
    return type == curToken.getType();
}

void Parser::match(TokenType type)
{
    if (!checkToken(type))
    {
        // abort("Expected " + type + ", got " + curToken.getType());
        abort("Expected another token");
    }
    nextToken();
}

void Parser::nextToken()
{
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
    /*
    Get libs here in future
    */
    while (!checkToken(TokenType::ENDOFFILE))
    {
        statement();
    }
}

void Parser::statement()
{
    std::vector<Token> new_statement;
    new_statement.push_back(curToken);
    
    nl();
}

void Parser::comparison()
{
    expression();
    if (isComparisonOperator())
    {
        // TODO
        nextToken();
        expression();
    }
    while (isComparisonOperator())
    {
        // TODO
        nextToken();
        expression();
    }
}

void Parser::expression()
{
    term();
    while (checkToken(TokenType::PLUS) || checkToken(TokenType::MINUS))
    {
        // TODO
        nextToken();
        term();
    }
}

void Parser::term()
{
    unary();
    while (checkToken(TokenType::ASTERISK) || checkToken(TokenType::SLASH))
    {
        // TODO
        nextToken();
        unary();
    }
}

void Parser::unary()
{
    if (checkToken(TokenType::PLUS) || checkToken(TokenType::MINUS))
    {
        // TODO
        nextToken();
    }
    primary();
}

void Parser::primary()
{
    if (checkToken(TokenType::NUMBER))
    {
        // TODO
        nextToken();
    }
    else if (checkToken(TokenType::IDENTIFIER))
    {
        // TODO
        nextToken();
    }
    else
    {
        abort("Unexpected token at " + curToken.getSource());
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
