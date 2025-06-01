#pragma once
#include "baseVariable.h"

/**
 * @class Integer
 * @brief Integer variable with arithmetic operation validation.
 */
class Integer :
    public BaseVariable<int, int> {
 public:
    /**
     * @brief Constructs a new Integer variable.
     * @param name Variable name
     * @param value Initial value
     * @param min Minimum value (default: INT_MIN)
     * @param max Maximum value (default: INT_MAX)
     * @throws std::invalid_argument If value is out of bounds
     */
     int min = INT_MIN;
     int max = INT_MAX;
    Integer();
    Integer(std::string& name);
    Integer(std::string& name, int value);

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
