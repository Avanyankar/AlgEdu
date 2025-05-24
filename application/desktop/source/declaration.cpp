#include <vector>
#include <stdexcept>
#include <string>
#include "declaration.h"
#include "tokenType.h"


bool Declaration::match(const std::vector<Token>& statement) const
{
	std::vector<TokenType> types;
	for (const auto token : statement)
	{
		types.push_back(token.getType());
	}
	if (types[0] != TokenType::LET)
	{
		return false;
	}
	if (types[1] != TokenType::IDENTIFIER)
	{
		throw std::invalid_argument("After LET considered to  be IDENTIFIER");
	}
	size_t i = 2;
	while (types[i] == TokenType::IDENTIFIER)
	{
		i++;
	}
	if (types[i] != TokenType::NEWLINE)
	{
		throw std::invalid_argument("After IDENTIFIER considered to  be NEWLINE");
	}
	return true;
}

void Declaration::instructions(std::vector<Token>& statement) const
{
	for (size_t i = 1; i < statement.size() - 1; i++)
	{
		std::string source = statement[i].getSource();
		auto pos = integers.find(source);
		if (pos != integers.end())
		{
			throw std::invalid_argument("Integer has been already declared");
		}
		integers[source] = Integer(source);
	}
}
