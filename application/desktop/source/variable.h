#pragma once

#include <climits>
#include <limits>
#include <stdexcept>
#include <string>

/**
 * @file variable.h
 * @brief Defines typed variable classes with range checking and operations.
 */

 /**
  * @class BaseVariable
  * @brief Templated base class for typed variables with bounds checking.
  * @tparam T Type of the variable's value.
  * @tparam B Type of the variable's bounds (min/max).
  */
template <typename T, typename B>
class BaseVariable {
public:
    std::string name; ///< Name of the variable (must be valid identifier)
    B min;           ///< Minimum allowed value
    B max;           ///< Maximum allowed value
    T value;         ///< Current value of the variable

    /**
     * @brief Constructs a new BaseVariable.
     * @param name Variable name (must be valid identifier)
     * @param value Initial value
     * @param min Minimum allowed value
     * @param max Maximum allowed value
     * @throws std::invalid_argument If:
     *   - min >= max
     *   - name is empty
     *   - name starts with digit or '_'
     *   - name contains invalid characters
     */
    BaseVariable(const std::string& name, T value, B min, B max);
};

/**
 * @class Integer
 * @brief Integer variable with arithmetic operation validation.
 */
class Integer : public BaseVariable<int, int> {
public:
    /**
     * @brief Constructs a new Integer variable.
     * @param name Variable name
     * @param value Initial value
     * @param min Minimum value (default: INT_MIN)
     * @param max Maximum value (default: INT_MAX)
     * @throws std::invalid_argument If value is out of bounds
     */
    Integer(const std::string& name, int value, int min = INT_MIN,
        int max = INT_MAX);

    /**
     * @brief Validates current value is within bounds.
     * @return true if min <= value <= max
     */
    bool validate() const;

    // Validation methods for arithmetic operations
    bool validate_addition(const Integer& other) const;
    bool validate_subtraction(const Integer& other) const;
    bool validate_multiplication(const Integer& other) const;
    bool validate_division(const Integer& other) const;
    bool validate_modulo_division(const Integer& other) const;

    // Compound assignment operators
    Integer& operator+=(const Integer& other);
    Integer& operator-=(const Integer& other);
    Integer& operator*=(const Integer& other);
    Integer& operator/=(const Integer& other);
    Integer& operator%=(const Integer& other);

    // Arithmetic operators
    Integer operator+(const Integer& other) const;
    Integer operator-(const Integer& other) const;
    Integer operator*(const Integer& other) const;
    Integer operator/(const Integer& other) const;
    Integer operator%(const Integer& other) const;
};

/**
 * @class String
 * @brief String variable with length bounds checking.
 */
class String : public BaseVariable<std::string, size_t> {
public:
    /**
     * @brief Constructs a new String variable.
     * @param name Variable name
     * @param value Initial value
     * @param min Minimum length (default: 0)
     * @param max Maximum length (default: size_t max)
     * @throws std::invalid_argument If:
     *   - min > max
     *   - length is out of bounds
     */
    String(const std::string& name, const std::string& value,
        size_t min = 0, size_t max = std::numeric_limits<size_t>::max());

    /**
     * @brief Validates current length is within bounds.
     * @return true if min <= length <= max
     */
    bool validate() const;

    /**
     * @brief Compound concatenation operator with length checking.
     * @param other The other string
     * @return Reference to modified object
     * @throws std::overflow_error If resulting length exceeds max
     */
    String& operator+=(const String& other);

    /**
     * @brief Concatenation operator with length checking.
     * @param other The other string
     * @return New String with combined value
     * @throws std::overflow_error If resulting length exceeds max
     */
    String operator+(const String& other) const;

    // Delete invalid string operations
    String operator-(const String& other) = delete;
    String operator*(const String& other) = delete;
    String operator/(const String& other) = delete;
    String operator%(const String& other) = delete;
};