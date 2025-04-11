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
    int default_value;
    int value;

    Variable(const std::string& name, int value, int min, int max, int default_value) : name(name), min(min), max(max), default_value(default_value), value(default_value)
    {
    }

    bool validate() const
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

    Variable operator+(const Variable another)
    {
        if  (!(validate_addition(another)))
        {
            long int abs = max;
            abs -= min;
            long int expression = value;
            expression += another.value;
            value = expression % abs;
            std::cerr << "Ошибка: переменная" << name << "переполнилась" << std::endl;
        }
        else
        {
            value += another.value;
        }
        return *this;
    }

    Variable operator-(const Variable another) 
    {
        if (!(validate_subtraction(another)))
        {
            long int expression = value;
            expression -= 2;
            value = max - (min - expression);
            std::cerr << "Ошибка: переменная" << name << "переполнилась" << std::endl;
        }
        else
        {
            value += another.value;
        }
        return *this;
    }

    Variable operator*(const Variable& other) const {
        return Variable(
            name + "*" + other.name,
            std::min(std::min(min * other.min, min * other.max),
                std::min(max * other.min, max * other.max)),
            std::max(std::max(min * other.min, min * other.max),
                std::max(max * other.min, max * other.max)),
            value * other.value
        );
    }

    Variable operator/(const Variable& other) const {
        return Variable(
            name + "/" + other.name,
            std::min(std::min(min / other.min, min / other.max),
                std::min(max / other.min, max / other.max)),
            std::max(std::max(min / other.min, min / other.max),
                std::max(max / other.min, max / other.max)),
            other.value != 0 ? value / other.value : 0
        );
    }

    Variable operator%(const Variable& other) const {
        return Variable(
            name + "%" + other.name,
            min,
            max,
            other.value != 0 ? value % other.value : 0
        );
    }
};

class Cell
{
public:
    int x;
    int y;
};

class Field
{
public:
    std::vector<std::vector<Cell>> cells;

    Field(int w = 0, int h = 0) : cells(h, std::vector<Cell>(w))
    {
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                cells[y][x] = { x, y };
    }

    ~Field()
    {

    }

    Cell& at(int x, int y)
    {
        return cells[y][x];
    }
};