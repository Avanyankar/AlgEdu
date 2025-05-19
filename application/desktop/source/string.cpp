#include "string.h"
#include <exception>
#include <iostream>

String::String(const std::string& name, const std::string& value,
    size_t min = 0, size_t max = std::numeric_limits<size_t>::max()) :
    BaseVariable<std::string, size_t>(name, value, min, max) {
    if (min > max) {
        throw std::invalid_argument("Минимальная длина превышает максимальную");
    }
    if (!validate()) {
        throw std::invalid_argument(
            "Длина строки '" + value + "' (" + std::to_string(value.length()) +
            ") выходит за границы [" + std::to_string(min) + ", " +
            std::to_string(max) + "]");
    }
}

bool String::validate() const {
    size_t length = value.length();
    return (length >= min) && (length <= max);
}

String& String::operator+=(const String& another) {
    std::string new_value = value + another.value;
    if (new_value.length() > max) {
        throw std::overflow_error("Превышена максимальная длина строки " + name);
    }
    value = new_value;
    return *this;
}

String String::operator+(const String& another) const {
    String result = *this;
    return result += another;
}

String String::operator-(const String& another) = delete;
String String::operator*(const String& another) = delete;
String String::operator/(const String& another) = delete;
String String::operator%(const String& another) = delete;
