#include "lexer.h"
#include <string>
#include <iostream>

class Lexer {
private:
    std::string source;
    char curChar;
    int curPos;

    void nextChar()
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

    void skipWhitespace()
    {
        while (this->curChar == ' ' || this->curChar == '\t' || this->curChar == '\r')
        {
            this->nextChar();
        }
    }

    void skipComment()
    {
        if (this->curChar == '#')
        {
            while (this->curChar != '\n' && this->curChar != '\0')
            {
                this->nextChar();
            }
        }
    }

    Token getToken()
    {
        this->skipWhitespace();
        this->skipComment();
        Token token;
        this->defineToken(token);
    }

    void defineToken(Token& token)
    {
        
    }

    void defineOperator(Token& token)
    {
        std::string source(&this->curChar);
        if (source == "+")
        {
            token.setType(TokenType::PLUS);
        }
        else if (source == "-")
        {
            token.setType(TokenType::MINUS);
        }
        else if (source == "*")
        {
            token.setType(TokenType::ASTERISK);
        }
        else if (source == "/")
        {
            token.setType(TokenType::SLASH);
        }
        else if (source == "=")
        {
            if (this->peek() == '=')
            {
                this->nextChar();
                source += this->curChar;
                token.setType(TokenType::EQEQ);
            }
            else
            {
                token.setType(TokenType::EQ);
            }
        }
        else if (source == ">")
        {
            if (this->peek() == '=')
            {
                this->nextChar();
                source += this->curChar;
                token.setType(TokenType::GTEQ);
            }
            else
            {
                token.setType(TokenType::GT);
            }
        }
        else if (source == "<")
        {
            if (this->peek() == '=')
            {
                this->nextChar();
                source += this->curChar;
                token.setType(TokenType::LTEQ);
            }
            else
            {
                token.setType(TokenType::LT);
            }
        }
    }
    
    char peek()
    {
        if (this->curPos + 1 >= this->source.size())
        {
            return '\0';
        }
        return this->source[this->curPos + 1];
    }

    void abort(const std::string& message)
    {
        std::cerr << "Lexing error. " << message << std::endl;
    }

public:
    Lexer (std::string source) {
        this->source = source + '\n';
        this->curChar = '\0';
        this->curPos = EOF;
        this->nextChar();
    }
};

class Token
{
private:
    std::string source;
    TokenType type;
public:
    Token ()
    {
        this->source = "";
        this->type = TokenType::NONE;
    }

    Token (std::string source, TokenType type)
    {
        this->source = source;
        this->type = type;
    }

    Token& setType(TokenType type)
    {
        this->type = type;
    }

    TokenType getType()
    {
        return this->type;
    }

    Token& setSource(std::string source)
    {
        this->source = source;
    }

    std::string getSource()
    {
        return this->source;
    }
};

enum class TokenType
{
    NONE,
    ENDOFFILE,
    NEWLINE,
    // Variables
    COLOR,
    NUMBER,
    IDENTIFIER,
    STRING,
    // Executor commands
    GO,
    GET,
    SCAN,
    // Keywords
    FILL,
    PRINT,
    LET,
    // If
    IF,
    THEN,
    ENDIF,
    // Cycles
    FOR,
    WHILE,
    DOWHILE,
    REPEAT,
    ENDFOR,
    ENDWHILE,
    ENDDOWHILE,
    // Operators
    EQ,
    PLUS,
    MINUS,
    ASTERISK,
    SLASH,
    EQEQ,
    NOTEQ,
    LT,
    LTEQ,
    GT,
    GTEQ,
    NOT
};
