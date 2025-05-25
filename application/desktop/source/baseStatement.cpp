#include <iostream>
#include "baseStatement.h"

bool BaseStatement::match_condition(const std::vector<Token>& statement, size_t* i) const
{
	if (!match_not_condition(statement, i))
	{
		return false;
	}
	while (statement[*i].getType() == TokenType::OR)
	{
		i++;
		if (!match_not_condition(statement, i))
		{
			throw std::invalid_argument("After OR considered to be NOT CONDITION");
		}
	}
	return true;
}

bool BaseStatement::match_not_condition(const std::vector<Token>& statement, size_t* i) const
{
	if (statement[*i].getType() == TokenType::NOT)
	{
		i++;
	}
	if (!match_and_condition(statement, i))
	{
		throw std::invalid_argument("After considered to be AND CONDITION");
	}
	i++;
	return true;
}

bool BaseStatement::match_and_condition(const std::vector<Token>& statement, size_t* i) const
{
	if (!match_comparison(statement, i))
	{
		return false;
	}
	while (statement[*i].getType() == TokenType::AND)
	{
		i++;
		if (!match_comparison(statement, i))
		{
			throw std::invalid_argument("After AND considered to be COMPARISON");
		}
	}
	return true;
}

bool BaseStatement::match_comparison(const std::vector<Token>& statement, size_t* i) const
{
	if (!match_expression(statement, i))
	{
		return false;
	}
	while (statement[*i].getType() == TokenType::LT || statement[*i].getType() == TokenType::LTEQ || 
		statement[*i].getType() == TokenType::GT || statement[*i].getType() == TokenType::GTEQ || 
		statement[*i].getType() == TokenType::EQEQ || statement[*i].getType() == TokenType::NOTEQ)
	{
		i++;
		if (!match_expression(statement, i))
		{
			throw std::invalid_argument("After COMPARISON OPERATOR considered to be EXPRESSION");
		}
	}
	return true;
}

bool BaseStatement::match_expression(const std::vector<Token>& statement, size_t* i) const
{
	if (!match_term(statement, i))
	{
		return false;
	}
	while (statement[*i].getType() == TokenType::PLUS || statement[*i].getType() == TokenType::MINUS)
	{
		i++;
		if (!match_term(statement, i))
		{
			throw std::invalid_argument("After PLUS or MINUS considered to be TERM");
		}
	}
	return true;
}

bool BaseStatement::match_term(const std::vector<Token>& statement, size_t* i) const
{
	if (!match_unary(statement, i))
	{
		return false;
	}
	while (statement[*i].getType() == TokenType::SLASH || statement[*i].getType() == TokenType::ASTERISK)
	{
		i++;
		if (!match_unary(statement, i))
		{
			throw std::invalid_argument("After ASTERISK or SLASH considered to be UNARY");
		}
	}
	return true;
}

bool BaseStatement::match_unary(const std::vector<Token>& statement, size_t* i) const
{
	if (statement[*i].getType() == TokenType::PLUS || statement[*i].getType() == TokenType::MINUS)
	{
		i++;
	}
	if (!match_primary(statement, i))
	{
		throw std::invalid_argument("After PLUS or MINUS considered to be PRIMARY");
	}
	i++;
	return true;
}

bool BaseStatement::match_primary(const std::vector<Token>& statement, size_t* i) const
{
	return (statement[*i].getType() == TokenType::NUMBER || statement[*i].getType() == TokenType::IDENTIFIER);
}

int BaseStatement::calculate_expression(const std::vector<Token>& statement, size_t* i) const
{
	if (statement[*i].getType() == TokenType::NUMBER)
	{
		int res = std::stoi(statement[*i].getSource());
	}
	else
	{
		int res = integers[statement[*i].getSource()].value;
	}
	i++;
	for (; *i < statement.size(); i++)
	{
		std::cout << "TODO";
	}
	return 0;
}
