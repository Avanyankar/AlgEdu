#include "integer.h"

Integer::Integer(const std::string& name, int min = INT_MIN, int max = INT_MAX) :
    BaseVariable<int, int>(name, min, max)
{
    if (!validate())
    {
        throw std::invalid_argument("�������� ������ ���� � ������ �������� � ���������");
    }
}

bool Integer::validate() const
{
    return value >= min && value <= max;
}

bool Integer::validate_addition(const Integer& another) const
{
    if (another.value > 0 && value > max - another.value) return false;
    if (another.value < 0 && value < min - another.value) return false;
    return true;
}

bool Integer::validate_subtraction(const Integer& another) const
{
    if (another.value < 0 && value > max + another.value) return false;
    if (another.value > 0 && value < min + another.value) return false;
    return true;
}

bool Integer::validate_multiplication(const Integer& another) const
{
    if (value == 0 || another.value == 0) return true;
    if ((value > 0) && ((another.value > 0 && value > max / another.value) ||
        (another.value < 0 && another.value < min / value)))
    {
        return false;
    }
    else if ((another.value > 0 && value < min / another.value) ||
        (another.value < 0 && value < max / another.value))
    {
        return false;
    }
    return true;
}

bool Integer::validate_division(const Integer& another) const
{
    return !(another.value == 0 || (value == min && another.value == -1));
}

bool Integer::validate_modulo_division(const Integer& another) const
{
    return (another.value != 0);
}

Integer& Integer::operator+=(const Integer& another)
{
    if (!validate_addition(another))
    {
        throw std::overflow_error("������������ ��� �������� " + name);
    }
    value += another.value;
    return *this;
}

Integer& Integer::operator-=(const Integer& another)
{
    if (!validate_subtraction(another))
    {
        throw std::overflow_error("������������ ��� ��������� " + name);
    }
    value -= another.value;
    return *this;
}

Integer& Integer::operator*=(const Integer& another)
{
    if (!validate_multiplication(another))
    {
        throw std::overflow_error("������������ ��� ��������� " + name);
    }
    value *= another.value;
    return *this;
}

Integer& Integer::operator/=(const Integer& another)
{
    if (another.value == 0)
    {
        throw std::runtime_error("������� �� ���� � ���������� " + name);
    }
    if (!validate_division(another))
    {
        throw std::overflow_error("������������ ��� ������� " + name);
    }
    value /= another.value;
    return *this;
}

Integer& Integer::operator%=(const Integer& another)
{
    if (another.value == 0)
    {
        throw std::runtime_error("������� �� ���� ��� ������ ������� � ���������� " + name);
    }
    if (!validate_modulo_division(another))
    {
        throw std::overflow_error("������������ ��� ������ ������� " + name);
    }
    value %= another.value;
    return *this;
}

Integer Integer::operator+(const Integer& another) const
{
    Integer result = *this;
    return result += another;
}

Integer Integer::operator-(const Integer& another) const
{
    Integer result = *this;
    return result -= another;
}

Integer Integer::operator*(const Integer& another) const
{
    Integer result = *this;
    return result *= another;
}

Integer Integer::operator/(const Integer& another) const
{
    Integer result = *this;
    return result /= another;
}

Integer Integer::operator%(const Integer& another) const
{
    Integer result = *this;
    return result %= another;
}
