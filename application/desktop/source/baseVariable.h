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
    std::string name;  ///< Name of the variable (must be valid identifier)
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
