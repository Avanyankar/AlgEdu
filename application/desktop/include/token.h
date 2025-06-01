#pragma once
#include <string>
#include "tokentype.h"

class Token
{
 private:
    std::string source;
    int type;
 public:
    Token();
    Token(std::string source, int type);
    void setType(int type);
    int getType();
    int getType() const;
    void setSource(std::string source);
    std::string getSource();
    std::string getSource() const;
};
