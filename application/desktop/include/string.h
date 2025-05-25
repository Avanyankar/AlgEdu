/* Disabled
#pragma once
#include "baseVariable.h"

/**
 * @class String
 * @brief String variable with length bounds checking.
 *
 /
class String :
    public BaseVariable<std::string, size_t> {
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
     *
     /
     size_t min = 0;
     size_t max = std::numeric_limits<size_t>::max();
     String(const std::string& name);
     String(const std::string& name, std::string value);

     /**
      * @brief Validates current length is within bounds.
      * @return true if min <= length <= max
      *
      /
     bool validate() const;

     /**
      * @brief Compound concatenation operator with length checking.
      * @param other The other string
      * @return Reference to modified object
      * @throws std::overflow_error If resulting length exceeds max
      *
      /
     String& operator+=(const String& other);

     /**
      * @brief Concatenation operator with length checking.
      * @param other The other string
      * @return New String with combined value
      * @throws std::overflow_error If resulting length exceeds max
      *
      /
     String operator+(const String& other) const;

     // Delete invalid string operations
     String operator-(const String& another) = delete;
     String operator*(const String& another) = delete;
     String operator/(const String& another) = delete;
     String operator%(const String& another) = delete;
};
*/
