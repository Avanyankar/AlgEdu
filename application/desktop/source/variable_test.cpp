// variable_classes_test.cpp
#include <gtest/gtest.h>
#include "variable.cpp"
#include <climits>

// Тесты для BaseVariable
class BaseVariableTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(BaseVariableTest, ConstructorValidation) {
    // Пустое имя
    EXPECT_THROW(BaseVariable<int, int>("", 0, 0, 1), std::invalid_argument);

    // Начинается с цифры
    EXPECT_THROW(BaseVariable<int, int>("1var", 0, 0, 1), std::invalid_argument);

    // Начинается с _
    EXPECT_THROW(BaseVariable<int, int>("_var", 0, 0, 1), std::invalid_argument);

    // Содержит недопустимый символ
    EXPECT_THROW(BaseVariable<int, int>("var@", 0, 0, 1), std::invalid_argument);

    // Корректное имя
    EXPECT_NO_THROW(BaseVariable<int, int>("validVar", 0, 0, 1));

    // min >= max
    EXPECT_THROW(BaseVariable<int, int>("var", 0, 1, 1), std::invalid_argument);
    EXPECT_THROW(BaseVariable<int, int>("var", 0, 2, 1), std::invalid_argument);
}

// Тесты для Integer
class IntegerTest : public ::testing::Test {
protected:
    void SetUp() override {
        intVar = new Integer("testInt", 10, 0, 100);
    }

    void TearDown() override {
        delete intVar;
    }

    Integer* intVar;
};

TEST_F(IntegerTest, ConstructorValidation) {
    // Значение на границе min
    EXPECT_THROW(Integer("atMin", 0, 0, 100), std::invalid_argument);

    // Значение на границе max
    EXPECT_THROW(Integer("atMax", 100, 0, 100), std::invalid_argument);

    // Значение вне диапазона
    EXPECT_THROW(Integer("belowMin", -1, 0, 100), std::invalid_argument);
    EXPECT_THROW(Integer("aboveMax", 101, 0, 100), std::invalid_argument);

    // Корректное значение
    EXPECT_NO_THROW(Integer("valid", 50, 0, 100));
}

TEST_F(IntegerTest, ValidateMethods) {
    Integer a("a", 50, 0, 100);
    Integer b("b", 60, 0, 100);

    // validate_addition
    EXPECT_TRUE(a.validate_addition(Integer("c", 10, 0, 100)));
    EXPECT_FALSE(a.validate_addition(Integer("d", 51, 0, 100)));

    // validate_subtraction
    EXPECT_TRUE(a.validate_subtraction(Integer("e", 10, 0, 100)));
    EXPECT_FALSE(Integer("f", -90, -100, 0).validate_subtraction(Integer("g", 11, 0, 100)));

    // validate_multiplication
    EXPECT_TRUE(a.validate_multiplication(Integer("h", 2, 0, 100)));
    EXPECT_FALSE(a.validate_multiplication(Integer("i", 3, 0, 100)));

    // validate_division
    EXPECT_TRUE(a.validate_division(Integer("j", 2, 0, 100)));
    EXPECT_FALSE(a.validate_division(Integer("k", 0, 0, 100)));

    // validate_modulo_division
    EXPECT_TRUE(a.validate_modulo_division(Integer("l", 2, 0, 100)));
    EXPECT_FALSE(a.validate_modulo_division(Integer("m", 0, 0, 100)));
}

TEST_F(IntegerTest, ArithmeticOperations) {
    Integer a("a", 50, 0, 100);
    Integer b("b", 30, 0, 100);

    // Сложение
    EXPECT_NO_THROW(a + b);
    EXPECT_THROW(Integer("c", 90, 0, 100) + Integer("d", 11, 0, 100), std::overflow_error);

    // Вычитание
    EXPECT_NO_THROW(a - b);
    EXPECT_THROW(Integer("e", -90, -100, 0) - Integer("f", 11, 0, 100), std::overflow_error);

    // Умножение
    EXPECT_NO_THROW(a * b);
    EXPECT_THROW(Integer("g", INT_MIN, INT_MIN, INT_MAX) * Integer("h", -1, INT_MIN, INT_MAX), std::overflow_error);

    // Деление
    EXPECT_NO_THROW(a / b);
    EXPECT_THROW(a / Integer("i", 0, 0, 100), std::runtime_error);
    EXPECT_THROW(Integer("j", INT_MIN, INT_MIN, INT_MAX) / Integer("k", -1, INT_MIN, INT_MAX), std::overflow_error);

    // Остаток от деления
    EXPECT_NO_THROW(a % b);
    EXPECT_THROW(a % Integer("l", 0, 0, 100), std::runtime_error);
}

// Тесты для String
class StringTest : public ::testing::Test {
protected:
    void SetUp() override {
        strVar = new String("testStr", "hello", 1, 100);
    }

    void TearDown() override {
        delete strVar;
    }

    String* strVar;
};

TEST_F(StringTest, ConstructorValidation) {
    // Пустая строка при min = 0
    EXPECT_NO_THROW(String("empty", "", 0, 100));

    // Пустая строка при min > 0
    EXPECT_THROW(String("empty", "", 1, 100), std::invalid_argument);

    // Слишком длинная строка
    EXPECT_THROW(String("long", std::string(101, 'a'), 0, 100), std::invalid_argument);

    // Корректная строка
    EXPECT_NO_THROW(String("valid", "test", 1, 100));
}

TEST_F(StringTest, Concatenation) {
    String a("a", "hello", 1, 10);
    String b("b", "world", 1, 10);

    // Успешная конкатенация
    EXPECT_NO_THROW(a + b);

    // Переполнение длины
    EXPECT_THROW(a + String("c", "verylongstring", 1, 10), std::overflow_error);
}

TEST_F(StringTest, DeletedOperations) {
    String a("a", "hello", 1, 10);
    String b("b", "world", 1, 10);

    // Проверка, что операции удалены
    EXPECT_TRUE(std::is_same<decltype(a.operator-(b)), void>::value);
    EXPECT_TRUE(std::is_same<decltype(a.operator*(b)), void>::value);
    EXPECT_TRUE(std::is_same<decltype(a.operator/(b)), void>::value);
    EXPECT_TRUE(std::is_same<decltype(a.operator%(b)), void>::value);
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}