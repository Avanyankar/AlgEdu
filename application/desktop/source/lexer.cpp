#include "lexer.h"
#include "token.h"
#include "tokenType.h"
#include <string>
#include <iostream>
#include <unordered_map>

const std::unordered_map<std::string, TokenType> Lexer::tokenMap = {
    // Special characters
    {"\n",  TokenType::NEWLINE},
    {"\0",  TokenType::ENDOFFILE},
    // операторы
    {"+",   TokenType::PLUS},
    {"-",   TokenType::MINUS},
    {"*",   TokenType::ASTERISK},
    {"/",   TokenType::SLASH},
    {"==",  TokenType::EQEQ},
    {"=",   TokenType::EQ},
    {">=",  TokenType::GTEQ},
    {">",   TokenType::GT},
    {"<=",  TokenType::LTEQ},
    {"<",   TokenType::LT},
    {"!=",  TokenType::NOTEQ},
    // Executor commands
    {"GO", TokenType::GO},
    {"GET", TokenType::GET},
    {"SCAN", TokenType::SCAN},
    {"FILL", TokenType::FILL},
    // Keywords
    {"PRINT", TokenType::PRINT},
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
    this->curPos += 1;
    if (this->curPos >= this->source.size())
    {
        this->curChar = '\0';
        this->curPos = EOF;
    }
    else 
    {
        this->curChar = this->source[this->curPos];
    }
}

void Lexer::skipWhitespace()
{
    while (this->curChar == ' ' || this->curChar == '\t' || this->curChar == '\r')
    {
        this->nextChar();
    }
}

void Lexer::skipComment()
{
    if (this->curChar == '#')
    {
        while (this->curChar != '\n' && this->curChar != '\0')
        {
            this->nextChar();
        }
    }
}

Token Lexer::getToken()
{
    this->skipWhitespace();
    this->skipComment();
    Token token;
    this->defineToken(token);
    return token;
}

void Lexer::defineToken(Token& token)
{
    std::string tokenSource(&this->curChar);
    while (true)
    {
        auto pos = tokenMap.find(tokenSource);
        if (pos != tokenMap.end())
        {

        }
        this->nextChar();
        tokenSource += this->curChar;
    }
    token.setSource(tokenSource);
}
    
char Lexer::peek()
{
    if (this->curPos + 1 >= this->source.size())
    {
        return '\0';
    }
    return this->source[this->curPos + 1];
}

void Lexer::abort(const std::string& message)
{
    std::cerr << "Lexing error. " << message << std::endl;
}

Lexer::Lexer(std::string source)
{
    this->source = source + '\n';
    this->curChar = '\0';
    this->curPos = EOF;
    this->nextChar();
}
