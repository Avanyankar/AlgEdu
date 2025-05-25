#include <iostream>
#include "../include/parser.h"
#include "../include/standardStatements.h"

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
    enabledStatements =
    {
        new Declaration,
        new Assignment,
    }; // Временная реализация
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
    Get enabledStatements here in future
    */
    while (!checkToken(TokenType::ENDOFFILE))
    {
        statement();
    }
}

void Parser::statement()
{
    // Упрощённая реализация для начала
    std::vector<Token> new_statement;
    while (peekToken.getType() != TokenType::NEWLINE)
    {
        new_statement.push_back(curToken);
        nextToken();
    }
    for (auto& statement : enabledStatements)
    {
        if (statement->match(new_statement))
        {
            statement->instructions(new_statement);
            nl();
            return;
        }
    }
    throw; // statement not in vector
}

void Parser::nl()
{
    match(TokenType::NEWLINE);
    while (checkToken(TokenType::NEWLINE))
    {
        nextToken();
    }
}
