#include <iostream>
#include "parser.h"
#include "standardStatements.h"

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

bool Parser::checkToken(int type)
{
    return curToken.getType() == type;
}

void Parser::match(int type)
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

void Parser::abort(const std::string& message)
{
    std::cerr << "Error! " << message << std::endl;
}

void Parser::program()
{
    while (checkToken(static_cast<int>(TokenType::NEWLINE)))
    {
        nextToken();
    }
    /*
    Get enabledStatements here in future
    */
    while (!checkToken(static_cast<int>(TokenType::ENDOFFILE)))
    {
        statement();
    }
}

void Parser::statement()
{
    // Упрощённая реализация для начала
    std::vector<Token> new_statement;
    while (peekToken.getType() != static_cast<int>(TokenType::NEWLINE))
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
    match(static_cast<int>(TokenType::NEWLINE));
    while (checkToken(static_cast<int>(TokenType::NEWLINE)))
    {
        nextToken();
    }
}
