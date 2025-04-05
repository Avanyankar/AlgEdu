#include "lexer.h"
#include <string>
#include <iostream>

class Lexer {
private:
    std::string source;
    char curChar;
    int curPos;

    Lexer& nextChar()
    {
        this->curPos += 1;
        if (this->curPos >= this->source.size()) {
            this->curChar = '\0';
            this->curPos = EOF;
        }
        else {
            this->curChar = this->source[this->curPos];
        }
        return *this;
    }

    Lexer& skipWhitespace()
    {
        while (this->curChar == ' ' || this->curChar == '\t' || this->curChar == '\r') {
            this->nextChar();
        }
        return *this;
    }

    Lexer& skipComment()
    {
        if (this->curChar == '#') {
            while (this->curChar != '\n' && this->curChar != '\0') {
                this->nextChar();
            }
        }
        return *this;
    }

    Token getToken()
    {

    }
    
    char peek()
    {
        if (this->curPos + 1 >= this->source.size()) return '\0';
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
    Token (std::string source, TokenType type)
    {
        this->source = source;
        this->type = type;
    }
};

enum class TokenType
{
    ENDOFILE,
    NEWLINE,
    NUMBER,
    IDENTIFIER,
    STRING,
    // Keywords
    PRINT,
    INPUT,
    LET,
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
