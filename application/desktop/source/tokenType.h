#pragma once

enum class TokenType
{
    NONE,
    // Special characters
    NEWLINE,
    ENDOFFILE,
    // Variables
    COLOR,
    NUMBER,
    IDENTIFIER,
    STRING,
    // Executor commands
    GO,
    GET,
    SCAN,
    FILL,
    // Keywords
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