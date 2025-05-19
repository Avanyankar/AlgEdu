#include "baseVariable.h"

template<typename T, typename B>
inline BaseVariable<T, B>::BaseVariable(const std::string& name, B min, B max) :
    name(name), min(min), max(max), value(value)
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
