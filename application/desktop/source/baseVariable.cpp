#include "baseVariable.h"

template<typename T, typename B>
BaseVariable<T, B>::BaseVariable()
{
}

template<typename T, typename B>
inline BaseVariable<T, B>::BaseVariable(std::string& _name) :
    name(_name)
{
    if (min >= max)
    {
        throw std::invalid_argument("������� ������ ���� ������ ���������");
    }
    if (name.empty())
    {
        throw std::invalid_argument("��� �� ����� ���� ������");
    }
    if (isdigit(name[0]))
    {
        throw std::invalid_argument("��� �� ����� ���������� � ����� ��� '_'");
    }
    for (char ch : name)
    {
        if (!isalnum(ch) && ch != '_')
        {
            throw std::invalid_argument(
                "��� �������� ������������ �������. ��������� ������ �����, ����� � _");
        }
    }
}

template<typename T, typename B>
BaseVariable<T, B>::BaseVariable(std::string& _name, T _value) :
    name(_name), value(_value)
{
}
