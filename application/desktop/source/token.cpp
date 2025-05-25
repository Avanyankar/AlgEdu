#include <iostream>
#include "token.h"

Token::Token()
{
    source = "";
    type = static_cast<int>(TokenType::NONE);
}

Token::Token(std::string _source, int _type) :
    source(_source), type(_type)
{
}

void Token::setType(int _type)
{
    type = _type;
}

int Token::getType()
{
    return type;
}

int Token::getType() const
{
    return type;
}

void Token::setSource(std::string _source)
{
    source = _source;
}

std::string Token::getSource()
{
    return source;
}

std::string Token::getSource() const
{
    return source;
}
