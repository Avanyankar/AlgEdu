#include "statement.h"
#include "variable.h"
#include <iostream>

void Statement::instructions(const std::vector<Token> statement)
{
	static_cast<const Statement*>(this)->instructions(statement);
}

void Statement::instructions(const std::vector<Token> statement) const
{
	if (declaration(statement))
	{
		return;
	}
	if (assignment(statement))
	{
		return;
	}
	if (print(statement))
	{
		return;
	}
	std::cerr << "Unexpected statement";
}

bool Statement::declaration(const std::vector<Token> statement)
{
	static_cast<const Statement*>(this)->declaration(statement);
}

bool Statement::declaration(const std::vector<Token> statement) const
{
	int i = 0;
	if (statement[i].getType() == TokenType::LET)
	{
		i++;
		while (statement[i].getType() != TokenType::NEWLINE)
		{
			integers[statement[i].getSource()] = Integer(statement[i].getSource(), NULL);
			i++;
		}
		return true;
	}
	return false;
}

bool Statement::assignment(const std::vector<Token> statement)
{
	static_cast<const Statement*>(this)->assignment(statement);
}

bool Statement::assignment(const std::vector<Token> statement) const
{
	int i = 0;
	if (statement[i].getType() == TokenType::IDENTIFIER)
	{
		i++;
		auto pos = integers.find(statement[i].getSource());
		if (pos == integers.end())
		{
			std::cerr << "The identifier wasn't declared.";
		}
		for (const auto& pair : integers)
		{
			if (pair.first == statement[i].getSource())
			{
				i++;
				if (statement[i].getType() == TokenType::EQ)
				{
					// TODO
				}
				else
				{
					std::cerr << "Expected \"=\".";
				}
			}
		}
	}
	return false;
}

bool Statement::print(const std::vector<Token> statement)
{
	static_cast<const Statement*>(this)->print(statement);
}

bool Statement::print(const std::vector<Token> statement) const
{
	int i = 0;
	if (statement[i].getSource() == "PRINT")
	{
		i++;
		while (statement[i].getType() != TokenType::NEWLINE)
		{
			if (statement[i].getType() == TokenType::STRING)
			{
				std::cout << statement[i].getSource() << " ";
			}
			if (statement[i].getType() == TokenType::IDENTIFIER)
			{
				std::cout << statement[i].getSource() << " ";
			}
			i++;
		}
		std::cout << std::endl;
		return true;
	}
	return false;
}

std::pair<std::vector<TokenType>, bool>& Statement::operator[](size_t index)
{
	if (index >= expected.size()) {
		throw std::out_of_range("Index out of range in Statement::operator[]");
	}
	return expected[index];
}

const std::pair<std::vector<TokenType>, bool>& Statement::operator[](size_t index) const
{
	if (index >= expected.size()) {
		throw std::out_of_range("Index out of range in Statement::operator[]");
	}
	return expected[index];
}

Statement::Statement(std::vector<std::pair<std::vector<TokenType>, bool>> _expected) : expected(_expected)
{
}
