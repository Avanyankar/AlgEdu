#include <vector>
#include <string>
#include <exception>
#include <iostream>
#include <climits>

class Variable
{
public:
    std::string name = "";
    int min = INT_MIN;
    int max = INT_MAX;
    int value;

    Variable(const std::string& name, int value, int min, int max) : name(name), min(min), max(max), value(value)
    {
        if (min >= max) 
        {
            throw std::invalid_argument("Минимум должен быть меньше максимума");
        }

        if (!validate()) 
        {
            throw std::invalid_argument("Значение должно быть в рамках минимума и максимума");
        }

        if (name.empty()) 
        {
            throw std::invalid_argument("Имя не может быть пустым");
        }

        if (isdigit(name[0]) || name[0] == '_') 
        {
            throw std::invalid_argument("Имя не может начинаться с цифры или '_'");
        }

        for (char c : name) 
        {
            if (!isalnum(c) && c != '_') 
            {
                throw std::invalid_argument("Имя содержит недопустимые символы. Разрешены только буквы, цифры и _");
            }
        }
    }

    bool validate()
    {
        return value > min && value < max;
    }

    bool validate_addition(Variable another) const
    {
        if (another.value > 0 && value > max - another.value) return false;
        if (another.value < 0 && value < min - another.value) return false;
        return true;
    }

    bool validate_subtraction(Variable another) const
    {
        if (another.value < 0 && value > max + another.value) return false;
        if (another.value > 0 && value < min + another.value) return false;
        return true;
    }

    bool validate_multiplication(Variable another) const
    {
        if (value == 0 || another.value == 0) return true;
        if ((value > 0) && ((another.value > 0 && value > max / another.value) || (another.value < 0 && another.value < min / value)))
        {
            return false;
        }
        else if ((another.value > 0 && value < min / another.value) || (another.value < 0 && value < max / another.value))
        {
            return false;
        }
        return true;
    }

    bool validate_division(Variable another) const
    {
        if ((another.value == 0) || (value == min && another.value == -1))
        {
            return false;
        }
        return true;
    }

    bool validate_modulo_division(Variable another) const
    {
        return (another.value != 0);
    }

    bool validate_addition(int number) const
    {
        if (number > 0 && value > max - number) return false;
        if (number < 0 && value < min - number) return false;
        return true;
    }

    bool validate_subtraction(int number) const
    {
        if (number < 0 && value > max + number) return false;
        if (number > 0 && value < min + number) return false;
        return true;
    }

    bool validate_multiplication(int number) const
    {
        if (value == 0 || number == 0) return true;
        if ((value > 0) && ((number > 0 && value > max / number) || (number < 0 && number < min / value)))
        {
            return false;
        }
        else if ((number > 0 && value < min / number) || (number < 0 && value < max / number))
        {
            return false;
        }
        return true;
    }

    bool validate_division(int number) const
    {
        if ((number == 0) || (value == min && number == -1))
        {
            return false;
        }
        return true;
    }

    bool validate_modulo_division(int number) const
    {
        return (number != 0);
    }

    Variable operator+(const Variable another)
    {
        if (!validate_addition(another))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при сложении");
        }
        value += another.value;
        return *this;
    }

    Variable operator-(const Variable another)
    {
        if (!validate_subtraction(another))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при вычитании");
        }
        value -= another.value;
        return *this;
    }

    Variable operator*(const Variable another)
    {
        if (!validate_multiplication(another))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при умножении");
        }
        value *= another.value;
        return *this;
    }

    Variable operator/(const Variable another)
    {
        if (another.value == 0)
        {
            throw std::runtime_error("Ошибка: деление на ноль в переменной " + name);
        }
        if (!validate_division(another))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при делении");
        }
        value /= another.value;
        return *this;
    }

    Variable operator%(const Variable another)
    {
        if (another.value == 0)
        {
            throw std::runtime_error("Ошибка: деление на ноль при взятии остатка в переменной " + name);
        }
        if (!validate_modulo_division(another))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при взятии остатка");
        }
        value %= another.value;
        return *this;
    }

    Variable operator+(int number)
    {
        if (!validate_addition(number))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при сложении");
        }
        value += number;
        return *this;
    }

    Variable operator-(int number)
    {
        if (!validate_subtraction(number))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при вычитании");
        }
        value -= number;
        return *this;
    }

    Variable operator*(int number)
    {
        if (!validate_multiplication(number))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при умножении");
        }
        value *= number;
        return *this;
    }

    Variable operator/(int number)
    {
        if (number == 0)
        {
            throw std::runtime_error("Ошибка: деление на ноль в переменной " + name);
        }
        if (!validate_division(number))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при делении");
        }
        value /= number;
        return *this;
    }

    Variable operator%(int number)
    {
        if (number == 0)
        {
            throw std::runtime_error("Ошибка: деление на ноль при взятии остатка в переменной " + name);
        }
        if (!validate_modulo_division(number))
        {
            throw std::overflow_error("Ошибка: переменная " + name + " переполнилась при взятии остатка");
        }
        value %= number;
        return *this;
    }
};

int main() {
    Variable a = Variable("a", 5, 0, 1000);
    Variable b = Variable("b", 1, 0, 1000);
    a = a / 0;
    std::cout << a.value;
}