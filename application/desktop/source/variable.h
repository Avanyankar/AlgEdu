#pragma once

#include <string>
#include <stdexcept>
#include <climits>
#include <vector>
#include <iostream>
#include <limits>

/**
 * @class Variable
 * @brief A class representing a variable with a constrained value range.
 *
 * This class allows storing an integer value within a specified range [min, max]
 * and performing arithmetic operations with overflow checks.
 */
class Variable {
public:
    /**
     * @brief Constructs a variable with specified name, value, and range.
     * @param name The name of the variable.
     * @param value The initial value.
     * @param min The minimum allowable value (default: INT_MIN).
     * @param max The maximum allowable value (default: INT_MAX).
     * @throws std::invalid_argument If the value is outside the allowable range.
     */
    Variable(const std::string& name, int value, int min = INT_MIN, int max = INT_MAX);

    /**
     * @brief Checks if the current value is within the allowable range.
     * @return True if the value is within [min, max], false otherwise.
     */
    bool validate() const;

    /**
     * @brief Validates if addition with another variable is possible without overflow.
     * @param another The other variable for the operation.
     * @return True if the operation is possible without overflow, false otherwise.
     */
    bool validate_addition(Variable another) const;

    /**
     * @brief Validates if subtraction with another variable is possible without overflow.
     * @param another The other variable for the operation.
     * @return True if the operation is possible without overflow, false otherwise.
     */
    bool validate_subtraction(Variable another) const;

    /**
     * @brief Validates if multiplication with another variable is possible without overflow.
     * @param another The other variable for the operation.
     * @return True if the operation is possible without overflow, false otherwise.
     */
    bool validate_multiplication(Variable another) const;

    /**
     * @brief Validates if division by another variable is possible.
     * @param another The other variable for the operation.
     * @return True if the operation is possible (no division by zero), false otherwise.
     */
    bool validate_division(Variable another) const;

    /**
     * @brief Validates if modulo division by another variable is possible.
     * @param another The other variable for the operation.
     * @return True if the operation is possible (no division by zero), false otherwise.
     */
    bool validate_modulo_division(Variable another) const;

    /**
     * @brief Addition operator.
     * @param another The other variable.
     * @return A new variable with the result of the operation.
     * @throws std::overflow_error If overflow occurs.
     */
    Variable operator+(Variable another);

    /**
     * @brief Subtraction operator.
     * @param another The other variable.
     * @return A new variable with the result of the operation.
     * @throws std::overflow_error If overflow occurs.
     */
    Variable operator-(Variable another);

    /**
     * @brief Multiplication operator.
     * @param another The other variable.
     * @return A new variable with the result of the operation.
     * @throws std::overflow_error If overflow occurs.
     */
    Variable operator*(Variable another);

    /**
     * @brief Division operator.
     * @param another The other variable.
     * @return A new variable with the result of the operation.
     * @throws std::overflow_error If overflow occurs.
     * @throws std::domain_error If division by zero occurs.
     */
    Variable operator/(Variable another);

    /**
     * @brief Modulo operator.
     * @param another The other variable.
     * @return A new variable with the result of the operation.
     * @throws std::overflow_error If overflow occurs.
     * @throws std::domain_error If division by zero occurs.
     */
    Variable operator%(Variable another);
};

/**
 * @class BaseVariable
 * @brief A templated base class for typed variables.
 * @tparam T The type of the variable's value.
 * @tparam B The type of the variable's bounds.
 */
template <typename T, typename B>
class BaseVariable {
public:
    /**
     * @brief Constructs a base variable with specified name, value, and bounds.
     * @param name The name of the variable.
     * @param value The initial value.
     * @param min The minimum allowable value.
     * @param max The maximum allowable value.
     * @throws std::invalid_argument If:
     * - min >= max
     * - name is empty
     * - name starts with a digit or '_'
     * - name contains invalid characters
     */
    BaseVariable(const std::string& name, T value, B min, B max);
};

/**
 * @class Integer
 * @brief A class for integer variables with range checking.
 *
 * Inherits from BaseVariable<int, int> and adds arithmetic operation checks.
 */
class Integer : public BaseVariable<int, int> {
public:
    /**
     * @brief Constructs an integer variable with specified name, value, and range.
     * @param name The name of the variable.
     * @param value The initial value.
     * @param min The minimum allowable value (default: INT_MIN).
     * @param max The maximum allowable value (default: INT_MAX).
     * @throws std::invalid_argument If the value is outside the allowable range.
     */
    Integer(const std::string& name, int value, int min = INT_MIN, int max = INT_MAX);

    /**
     * @brief Checks if the value is within the allowable range.
     * @return True if the value is within (min, max), false otherwise.
     */
    bool validate();

    /**
     * @brief Validates if addition is possible without overflow.
     * @param another The other variable for addition.
     * @return True if addition is possible without overflow, false otherwise.
     */
    bool validate_addition(Integer another) const;

    /**
     * @brief Validates if subtraction is possible without overflow.
     * @param another The other variable for subtraction.
     * @return True if subtraction is possible without overflow, false otherwise.
     */
    bool validate_subtraction(Integer another) const;

    /**
     * @brief Validates if multiplication is possible without overflow.
     * @param another The other variable for multiplication.
     * @return True if multiplication is possible without overflow, false otherwise.
     */
    bool validate_multiplication(Integer another) const;

    /**
     * @brief Validates if division is possible.
     * @param another The divisor.
     * @return True if division is possible (no division by zero or overflow), false otherwise.
     */
    bool validate_division(Integer another) const;

    /**
     * @brief Validates if modulo division is possible.
     * @param another The divisor.
     * @return True if modulo division is possible (no division by zero), false otherwise.
     */
    bool validate_modulo_division(Integer another) const;

    /**
     * @brief Addition operator.
     * @param another The other integer variable.
     * @return Reference to this object after addition.
     * @throws std::overflow_error If overflow occurs.
     */
    Integer operator+(const Integer another);

    /**
     * @brief Subtraction operator.
     * @param another The other integer variable.
     * @return Reference to this object after subtraction.
     * @throws std::overflow_error If overflow occurs.
     */
    Integer operator-(const Integer another);

    /**
     * @brief Multiplication operator.
     * @param another The other integer variable.
     * @return Reference to this object after multiplication.
     * @throws std::overflow_error If overflow occurs.
     */
    Integer operator*(const Integer another);

    /**
     * @brief Division operator.
     * @param another The divisor.
     * @return Reference to this object after division.
     * @throws std::runtime_error If division by zero occurs.
     * @throws std::overflow_error If overflow occurs.
     */
    Integer operator/(const Integer another);

    /**
     * @brief Modulo operator.
     * @param another The divisor.
     * @return Reference to this object after modulo operation.
     * @throws std::runtime_error If division by zero occurs.
     * @throws std::overflow_error If overflow occurs.
     */
    Integer operator%(const Integer another);
};

/**
 * @class String
 * @brief A class for string variables with length checking.
 *
 * Inherits from BaseVariable<std::string, size_t> and adds string operation checks.
 */
class String : public BaseVariable<std::string, size_t> {
public:
    /**
     * @brief Constructs a string variable with specified name, value, and length bounds.
     * @param name The name of the variable.
     * @param value The initial string value.
     * @param min The minimum allowable length (default: 0).
     * @param max The maximum allowable length (default: size_t max).
     * @throws std::invalid_argument If:
     * - min > max
     * - string length is outside the allowable range
     */
    String(const std::string& name, const std::string& value, size_t min = 0, size_t max = std::numeric_limits<size_t>::max());

    /**
     * @brief Checks if the string length is within the allowable range.
     * @return True if the length is within [min, max], false otherwise.
     */
    bool validate() const;

    /**
     * @brief String concatenation operator.
     * @param another The other string variable.
     * @return A new string variable with the result of concatenation.
     * @throws std::overflow_error If the resulting length exceeds max.
     */
    String operator+(const String& another) const;

    /**
     * @brief Deleted subtraction operator (not applicable for strings).
     */
    String operator-(const String& another) = delete;

    /**
     * @brief Deleted multiplication operator (not applicable for strings).
     */
    String operator*(const String& another) = delete;

    /**
     * @brief Deleted division operator (not applicable for strings).
     */
    String operator/(const String& another) = delete;

    /**
     * @brief Deleted modulo operator (not applicable for strings).
     */
    String operator%(const String& another) = delete;
};