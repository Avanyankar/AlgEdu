#include "parser.h"
#include <iostream>
#include <cstdlib>
#include "stdLib.h"

Parser::Parser(Lexer* lexer, Emitter* emitter)
{
    this->lexer = lexer;
    this->emitter = emitter;
    this->curToken;
    this->peekToken;
    this->libs.push_back(StdLib());
    nextToken();
    nextToken();
 }

bool Parser::checkToken(TokenType type)
{
    return type == curToken.getType();
}

bool Parser::checkPeek(TokenType type)
{
    return type == peekToken.getType();
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
    for (const auto& lib : libs)
    {
        for (const auto& statement : lib.statements)
        {
            bool flag = false;
            for (const auto& expected_types : statement.expected)
            {
                flag = false;
                for (const auto& expected_type : expected_types)
                {
                    flag = checkToken(expected_type);
                    if (flag)
                    {
                        break;
                    }
                }
                if (!flag)
                {
                    break;
                }
                nextToken();
                new_statement.push_back(curToken);
            }
            if (!flag)
            {
                break;
            }
            statement.instructions(new_statement);
            break;
        }
    }
    nl();
}

void Parser::comparison()
{
    expression();
    if (isComparisonOperator())
    {
        // emitter.emit('...');
        nextToken();
        expression();
    }
    while (isComparisonOperator())
    {
        // emitter.emit('...');
        nextToken();
        expression();
    }
}

void Parser::expression()
{
    term();
    while (checkToken(TokenType::PLUS) || checkToken(TokenType::MINUS))
    {
        // emitter.emit('...');
        nextToken();
        term();
    }
}

void Parser::term()
{
    unary();
    while (checkToken(TokenType::ASTERISK) || checkToken(TokenType::SLASH))
    {
        // emitter.emit('...');
        nextToken();
        unary();
    }
}

void Parser::unary()
{
    if (checkToken(TokenType::PLUS) || checkToken(TokenType::MINUS))
    {
        // emitter.emit('...');
        nextToken();
    }
    primary();
}

void Parser::primary()
{
    if (checkToken(TokenType::NUMBER))
    {
        // emitter.emit(curToken.getSource());
        nextToken();
    }
    else if (checkToken(TokenType::IDENTIFIER))
    {
        if (symbols.find(curToken.getSource()) == symbols.end())
        {
            abort("Referencing variable before assignment: " + curToken.getSource());
        }
        // emitter.emit('...');
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
