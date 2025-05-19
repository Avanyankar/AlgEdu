#include <iostream>
#include "token.h"

Token::Token()
{
    source = "";
    type = TokenType::NONE;
}

Token::Token(std::string _source, TokenType _type) :
    source(_source), type(_type)
{
}

void Token::setType(TokenType type)
{
    type = type;
}

TokenType Token::getType()
{
    return type;
}

TokenType Token::getType() const
{
    return type;
}

void Token::setSource(std::string source)
{
    source = source;
}

std::string Token::getSource()
{
    return source;
}

std::string Token::getSource() const
{
    return source;
}
