#include "token.h"
#include "tokentype.h"
#include <string>
#include <iostream>

Token::Token()
{
    this->source = "";
    this->type = TokenType::NONE;
}

Token::Token(std::string source, TokenType type)
{
    this->source = source;
    this->type = type;
}

void Token::setType(TokenType type)
{
    this->type = type;
}

TokenType Token::getType()
{
    return this->type;
}

void Token::setSource(std::string source)
{
    this->source = source;
}

std::string Token::getSource()
{
    return this->source;
}