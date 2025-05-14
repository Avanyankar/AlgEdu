#include <string>
#include <exception>
#include <iostream>
#include <climits>
#include <limits>

template <typename T, typename B>
class BaseVariable {
public:
    std::string name;
    B min;
    B max;
    T value;

    BaseVariable(const std::string& name, T value, B min, B max)
        : name(name), min(min), max(max), value(value) {
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
};

class Integer : public BaseVariable<int, int> {
public:
    Integer(const std::string& name, int value, int min = INT_MIN, int max = INT_MAX)
        : BaseVariable<int, int>(name, value, min, max) {
        if (!validate()) {
            throw std::invalid_argument("Значение должно быть в рамках минимума и максимума");
        }
    }

    bool validate() const {
        return value >= min && value <= max;
    }

    bool validate_addition(const Integer& another) const {
        if (another.value > 0 && value > max - another.value) return false;
        if (another.value < 0 && value < min - another.value) return false;
        return true;
    }

    bool validate_subtraction(const Integer& another) const {
        if (another.value < 0 && value > max + another.value) return false;
        if (another.value > 0 && value < min + another.value) return false;
        return true;
    }

    bool validate_multiplication(const Integer& another) const {
        if (value == 0 || another.value == 0) return true;
        if ((value > 0) && ((another.value > 0 && value > max / another.value) ||
            (another.value < 0 && another.value < min / value))) {
            return false;
        }
        else if ((another.value > 0 && value < min / another.value) ||
            (another.value < 0 && value < max / another.value)) {
            return false;
        }
        return true;
    }

    bool validate_division(const Integer& another) const {
        return !(another.value == 0 || (value == min && another.value == -1));
    }

    bool validate_modulo_division(const Integer& another) const {
        return (another.value != 0);
    }

    Integer& operator+=(const Integer& another) {
        if (!validate_addition(another)) {
            throw std::overflow_error("Переполнение при сложении " + name);
        }
        value += another.value;
        return *this;
    }

    Integer& operator-=(const Integer& another) {
        if (!validate_subtraction(another)) {
            throw std::overflow_error("Переполнение при вычитании " + name);
        }
        value -= another.value;
        return *this;
    }

    Integer& operator*=(const Integer& another) {
        if (!validate_multiplication(another)) {
            throw std::overflow_error("Переполнение при умножении " + name);
        }
        value *= another.value;
        return *this;
    }

    Integer& operator/=(const Integer& another) {
        if (another.value == 0) {
            throw std::runtime_error("Деление на ноль в переменной " + name);
        }
        if (!validate_division(another)) {
            throw std::overflow_error("Переполнение при делении " + name);
        }
        value /= another.value;
        return *this;
    }

    Integer& operator%=(const Integer& another) {
        if (another.value == 0) {
            throw std::runtime_error("Деление на ноль при взятии остатка в переменной " + name);
        }
        if (!validate_modulo_division(another)) {
            throw std::overflow_error("Переполнение при взятии остатка " + name);
        }
        value %= another.value;
        return *this;
    }

    Integer operator+(const Integer& another) const {
        Integer result = *this;
        return result += another;
    }

    Integer operator-(const Integer& another) const {
        Integer result = *this;
        return result -= another;
    }

    Integer operator*(const Integer& another) const {
        Integer result = *this;
        return result *= another;
    }

    Integer operator/(const Integer& another) const {
        Integer result = *this;
        return result /= another;
    }

    Integer operator%(const Integer& another) const {
        Integer result = *this;
        return result %= another;
    }
};

class String : public BaseVariable<std::string, size_t> {
public:
    String(const std::string& name, const std::string& value,
        size_t min = 0, size_t max = std::numeric_limits<size_t>::max())
        : BaseVariable<std::string, size_t>(name, value, min, max) {
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

    bool validate() const {
        size_t length = value.length();
        return (length >= min) && (length <= max);
    }

    String& operator+=(const String& another) {
        std::string new_value = value + another.value;
        if (new_value.length() > max) {
            throw std::overflow_error("Превышена максимальная длина строки " + name);
        }
        value = new_value;
        return *this;
    }

    String operator+(const String& another) const {
        String result = *this;
        return result += another;
    }

    String operator-(const String& another) = delete;
    String operator*(const String& another) = delete;
    String operator/(const String& another) = delete;
    String operator%(const String& another) = delete;
};