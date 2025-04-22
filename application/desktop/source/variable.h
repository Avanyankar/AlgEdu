#ifndef VARIABLE_H
#define VARIABLE_H

#include <string>
#include <stdexcept>
#include <climits>

class Variable
{
public:
    std::string name;
    int min;
    int max;
    int value;

    // Конструктор
    Variable(const std::string& name, int value, int min = INT_MIN, int max = INT_MAX);

    // Валидация значений
    bool validate() const;
    bool validate_addition(Variable another) const;
    bool validate_subtraction(Variable another) const;
    bool validate_multiplication(Variable another) const;
    bool validate_division(Variable another) const;
    bool validate_modulo_division(Variable another) const;

    // Операторы
    Variable operator+(Variable another);
    Variable operator-(Variable another);
    Variable operator*(Variable another);
    Variable operator/(Variable another);
    Variable operator%(Variable another);
};

#endif