#pragma once

#include <string>
#include <stdexcept>
#include <climits>

/**
 * @class Variable
 * @brief Класс, представляющий переменную с ограниченным диапазоном значений.
 *
 * Позволяет хранить целочисленное значение в заданном диапазоне [min, max]
 * и выполнять арифметические операции с проверкой переполнений.
 */
class Variable
{
public:
    std::string name;  ///< Название переменной
    int min;           ///< Минимально допустимое значение
    int max;           ///< Максимально допустимое значение
    int value;         ///< Текущее значение переменной

    /**
     * @brief Конструктор переменной
     * @param name Имя переменной
     * @param value Начальное значение
     * @param min Минимальное допустимое значение (по умолчанию INT_MIN)
     * @param max Максимальное допустимое значение (по умолчанию INT_MAX)
     * @throw std::invalid_argument Если значение выходит за допустимые границы
     */
    Variable(const std::string& name, int value, int min = INT_MIN, int max = INT_MAX);

    /**
     * @brief Проверяет, находится ли текущее значение в допустимом диапазоне
     * @return true если значение в пределах [min, max], иначе false
     */
    bool validate() const;

    /**
     * @brief Проверяет возможность сложения с другой переменной без переполнения
     * @param another Другая переменная для операции
     * @return true если операция возможна без переполнения, иначе false
     */
    bool validate_addition(Variable another) const;

    /**
     * @brief Проверяет возможность вычитания другой переменной без переполнения
     * @param another Другая переменная для операции
     * @return true если операция возможна без переполнения, иначе false
     */
    bool validate_subtraction(Variable another) const;

    /**
     * @brief Проверяет возможность умножения на другую переменную без переполнения
     * @param another Другая переменная для операции
     * @return true если операция возможна без переполнения, иначе false
     */
    bool validate_multiplication(Variable another) const;

    /**
     * @brief Проверяет возможность деления на другую переменную
     * @param another Другая переменная для операции
     * @return true если операция возможна (деление на ноль исключено), иначе false
     */
    bool validate_division(Variable another) const;

    /**
     * @brief Проверяет возможность взятия модуля от деления
     * @param another Другая переменная для операции
     * @return true если операция возможна (деление на ноль исключено), иначе false
     */
    bool validate_modulo_division(Variable another) const;

    /**
     * @brief Оператор сложения
     * @param another Другая переменная
     * @return Новая переменная с результатом операции
     * @throw std::overflow_error Если происходит переполнение
     */
    Variable operator+(Variable another);

    /**
     * @brief Оператор вычитания
     * @param another Другая переменная
     * @return Новая переменная с результатом операции
     * @throw std::overflow_error Если происходит переполнение
     */
    Variable operator-(Variable another);

    /**
     * @brief Оператор умножения
     * @param another Другая переменная
     * @return Новая переменная с результатом операции
     * @throw std::overflow_error Если происходит переполнение
     */
    Variable operator*(Variable another);

    /**
     * @brief Оператор деления
     * @param another Другая переменная
     * @return Новая переменная с результатом операции
     * @throw std::overflow_error Если происходит переполнение
     * @throw std::domain_error При делении на ноль
     */
    Variable operator/(Variable another);

    /**
     * @brief Оператор взятия модуля от деления
     * @param another Другая переменная
     * @return Новая переменная с результатом операции
     * @throw std::overflow_error Если происходит переполнение
     * @throw std::domain_error При делении на ноль
     */
    Variable operator%(Variable another);
};