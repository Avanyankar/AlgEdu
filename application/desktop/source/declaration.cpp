#include <vector>
#include <stdexcept>
#include <string>
#include "declaration.h"
#include "tokenType.h"


bool Declaration::match(const std::vector<Token>& statement) const
{
	std::vector<TokenType> types;
	std::vector<std::string> names;
	for (const auto token : statement)
	{
		types.push_back(token.getType());
		names.push_back(token.getSource());
	}
	if (types[0] != TokenType::LET)
	{
		return false;
	}
	if (types[1] != TokenType::IDENTIFIER)
	{
		throw std::invalid_argument("After LET should be IDENTIFIER");
	}
	integers[names[1]] = Integer();
	int i = 2;
	if (types[i] == TokenType::IDENTIFIER)
	{
		i++;
	}
}
