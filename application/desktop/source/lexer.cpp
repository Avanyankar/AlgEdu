#include <regex>
#include <iostream>
#include "lexer.h"

const std::unordered_map<std::string, TokenType> Lexer::tokenMap = {
    // Special characters
    {"\n", TokenType::NEWLINE},
    {"\0", TokenType::ENDOFFILE},
    // Variables
    {"\"RED\" | \"GREEN\" | \"BLUE\" | \"YELLOW\" | \"WHITE\" | \"BLACK\"", TokenType::COLOR},
    {"[0-9]+", TokenType::NUMBER},
    {"[a-zA-Z_][a-zA-Z0-9_]*", TokenType::IDENTIFIER},
    {"\"[^\"]*\"", TokenType::STRING},
    // Operators
    {"+", TokenType::PLUS},
    {"-", TokenType::MINUS},
    {"*", TokenType::ASTERISK},
    {"/", TokenType::SLASH},
    {"==", TokenType::EQEQ},
    {"=", TokenType::EQ},
    {">=", TokenType::GTEQ},
    {">", TokenType::GT},
    {"<=", TokenType::LTEQ},
    {"<", TokenType::LT},
    {"!=", TokenType::NOTEQ},
    {"NOT", TokenType::NOT},
    {"AND", TokenType::AND},
    {"OR", TokenType::OR},
    // Executor commands
    {"GO", TokenType::GO},
    {"GET", TokenType::GET},
    {"SCAN", TokenType::SCAN},
    {"FILL", TokenType::FILL},
    // Keywords
    {"PRINT", TokenType::PRINT},
    {"INPUT", TokenType::PRINT},
    {"LET", TokenType::LET},
    // If
    {"IF", TokenType::IF},
    {"THEN", TokenType::THEN},
    {"ENDIF", TokenType::ENDIF},
    // Cycles
    {"FOR", TokenType::FOR},
    {"WHILE", TokenType::WHILE},
    {"DOWHILE", TokenType::DOWHILE},
    {"REPEAT", TokenType::REPEAT},
    {"ENDFOR", TokenType::ENDFOR},
    {"ENDWHILE", TokenType::ENDWHILE},
    {"ENDDOWHILE", TokenType::ENDDOWHILE},
};

void Lexer::nextChar()
{
    curPos += 1;
    if (curPos >= source.size())
    {
        curChar = '\0';
        curPos = EOF;
    }
    else
    {
        curChar = source[curPos];
    }
}

void Lexer::skipWhitespace()
{
    while (curChar == ' ' || curChar == '\t' || curChar == '\r')
    {
        nextChar();
    }
}

void Lexer::skipComment()
{
    if (curChar == '#')
    {
        while (curChar != '\n' && curChar != '\0')
        {
            nextChar();
        }
    }
}

Token Lexer::getToken()
{
    skipWhitespace();
    skipComment();
    Token token;
    defineToken(token);
    return token;
}

Lexer* Lexer::getInstance(std::string source)
{
    if (instance == nullptr)
    {
        instance = new Lexer(source);
    }
    return instance;
}

void Lexer::defineToken(Token& token)
{
    std::string tokenSource(&curChar);
    while (true)
    {
        auto pos = tokenMap.find(tokenSource);
        if (pos != tokenMap.end())
        {
            TokenType type = pos->second;
            if (type == TokenType::COLOR || type == TokenType::IDENTIFIER ||
                type == TokenType::NUMBER || type == TokenType::STRING)
            {
                abort("Expected token, received regex.");
            }
            token.setType(type);
            break;
        }
        nextChar();
        if (curChar == ' ' || curChar == '#' || curChar == '\r' ||
            curChar == '\t' || curChar == '\0' || curChar == '\n')
        {
            std::string colorPattern, numberPattern, identifierPattern, stringPattern;
            for (const auto& pair : tokenMap)
            {
                switch (pair.second)
                {
                case TokenType::COLOR:
                    colorPattern = pair.first;
                    break;
                case TokenType::NUMBER:
                    numberPattern = pair.first;
                    break;
                case TokenType::IDENTIFIER:
                    identifierPattern = pair.first;
                    break;
                case TokenType::STRING:
                    stringPattern = pair.first;
                    break;
                default:
                    break;
                }
            }
            std::regex colorRegex(colorPattern);
            if (std::regex_match(tokenSource, colorRegex))
            {
                token.setType(TokenType::COLOR);
                break;
            }
            std::regex numberRegex(numberPattern);
            if (std::regex_match(tokenSource, numberRegex))
            {
                token.setType(TokenType::NUMBER);
                break;
            }
            std::regex identifierRegex(identifierPattern);
            if (std::regex_match(tokenSource, identifierRegex))
            {
                token.setType(TokenType::IDENTIFIER);
                break;
            }
            std::regex stringRegex(stringPattern);
            if (std::regex_match(tokenSource, stringRegex))
            {
                token.setType(TokenType::STRING);
                break;
            }
            abort("Expected token, received regex.");
        }
        tokenSource += curChar;
    }
    token.setSource(tokenSource);
}

char Lexer::peek()
{
    if (curPos + 1 >= source.size())
    {
        return '\0';
    }
    return source[curPos + 1];
}

void Lexer::abort(const std::string& message)
{
    std::cerr << "Lexing error. " << message << std::endl;
}

Lexer::Lexer(std::string _source)
{
    source = _source + '\n';
    curChar = '\0';
    curPos = EOF;
    nextChar();
}
