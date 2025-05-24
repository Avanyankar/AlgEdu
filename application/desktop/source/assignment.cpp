#include "../include/assignment.h"

bool Assignment::match(const std::vector<Token>& statement) const
{
	std::vector<TokenType> types;
	for (const auto token : statement)
	{
		types.push_back(token.getType());
	}
	if (types[0] != TokenType::IDENTIFIER)
	{
		return false;
	}
	if (types[1] != TokenType::EQ)
	{
		throw std::invalid_argument("After IDENTIFIER considered to be EQ");
	}
	size_t i = 2;
	if (!match_expression(statement, &i))
	{
		throw std::invalid_argument("After EQ considered to be expression");
	}
	if (types[i] != TokenType::NEWLINE)
	{
		throw std::invalid_argument("After IDENTIFIER considered to be NEWLINE");
	}
	return true;
}

void Assignment::instructions(std::vector<Token>& statement) const
{
	// integers[statement[0].getSource()] = calculate_expression()
}
