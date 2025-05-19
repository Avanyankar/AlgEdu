#include "baseVariable.h"

template<typename T, typename B>
inline BaseVariable<T, B>::BaseVariable(const std::string& name, T value, B min, B max) :
    name(name), min(min), max(max), value(value)
{
    if (min >= max) {
        throw std::invalid_argument("Минимум должен быть меньше максимума");
    }

    if (name.empty()) {
        throw std::invalid_argument("Имя не может быть пустым");
    }

    if (isdigit(name[0]) || name[0] == '_') {
        throw std::invalid_argument("Имя не может начинаться с цифры или '_'");
    }

    for (char c : name) {
        if (!isalnum(c) && c != '_') {
            throw std::invalid_argument(
                "Имя содержит недопустимые символы. Разрешены только буквы, цифры и _");
        }
    }
}