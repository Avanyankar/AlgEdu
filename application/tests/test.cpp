#include "pch.h"
#include "../desktop/source/variable.cpp"

// ==================== Integer Tests ====================

TEST(IntegerTest, ValidConstructor) 
{
    EXPECT_NO_THROW(Integer("valid", 5, 0, 10));
}

TEST(IntegerTest, EmptyNameThrows) 
{
    EXPECT_THROW(Integer("", 5), std::invalid_argument);
}

TEST(IntegerTest, NameStartsWithDigitThrows) 
{
    EXPECT_THROW(Integer("1var", 5), std::invalid_argument);
}

TEST(IntegerTest, NameStartsWithUnderscoreThrows) 
{
    EXPECT_THROW(Integer("_var", 5), std::invalid_argument);
}

TEST(IntegerTest, InvalidCharsInNameThrows) 
{
    EXPECT_THROW(Integer("var-name", 5), std::invalid_argument);
}

TEST(IntegerTest, MinNotLessThanMaxThrows) 
{
    EXPECT_THROW(Integer("var", 5, 10, 5), std::invalid_argument);
    EXPECT_THROW(Integer("var", 5, 10, 10), std::invalid_argument);
}

TEST(IntegerTest, ValueOutOfRangeThrows) 
{
    EXPECT_THROW(Integer("var", 15, 0, 10), std::invalid_argument);
}

TEST(IntegerTest, AdditionWithinRange) 
{
    Integer a("a", 5, 0, 10);
    Integer b("b", 3);
    EXPECT_NO_THROW(a + b);
    EXPECT_EQ((a + b).value, 8);
}

TEST(IntegerTest, AdditionOverflowThrows) 
{
    Integer a("a", INT_MAX);
    Integer b("b", 1);
    EXPECT_THROW(a + b, std::overflow_error);
}

TEST(IntegerTest, SubtractionWithinRange) 
{
    Integer a("a", 5);
    Integer b("b", 3);
    EXPECT_NO_THROW(a - b);
    EXPECT_EQ((a - b).value, 2);
}

TEST(IntegerTest, SubtractionUnderflowThrows) 
{
    Integer a("a", INT_MIN);
    Integer b("b", 1);
    EXPECT_THROW(a - b, std::overflow_error);
}

TEST(IntegerTest, DivisionByZeroThrows) 
{
    Integer a("a", 5);
    Integer zero("zero", 0);
    EXPECT_THROW(a / zero, std::runtime_error);
}

// ==================== String Tests ====================

TEST(StringTest, ValidConstructor) 
{
    EXPECT_NO_THROW(String("valid", "test", 0, 10));
}

TEST(StringTest, EmptyNameThrows) 
{
    EXPECT_THROW(String("", "test"), std::invalid_argument);
}

TEST(StringTest, StringLengthBelowMinThrows) 
{
    EXPECT_THROW(String("var", "hi", 3, 10), std::invalid_argument);
}

TEST(StringTest, StringLengthAboveMaxThrows) 
{
    EXPECT_THROW(String("var", "too long", 0, 5), std::invalid_argument);
}

TEST(StringTest, ConcatenationWithinRange) 
{
    String a("a", "hello", 0, 20);
    String b("b", " world");
    String result = a + b;
    EXPECT_EQ(result.value, "hello world");
}

TEST(StringTest, ConcatenationOverflowThrows) 
{
    String a("a", "long", 0, 5);
    String b("b", "string");
    EXPECT_THROW(a + b, std::overflow_error);
}

// Тесты для удалённых операторов
template<typename T>
class has_subtraction 
{
    template<typename U>
    static auto test(int) -> decltype(std::declval<U>() - std::declval<U>(), std::true_type{});

    template<typename>
    static std::false_type test(...);

public:
    static constexpr bool value = decltype(test<T>(0))::value;
};

template<typename T>
class has_multiplication 
{
    template<typename U>
    static auto test(int) -> decltype(std::declval<U>()* std::declval<U>(), std::true_type{});

    template<typename>
    static std::false_type test(...);

public:
    static constexpr bool value = decltype(test<T>(0))::value;
};

template<typename T>
class has_division 
{
    template<typename U>
    static auto test(int) -> decltype(std::declval<U>() / std::declval<U>(), std::true_type{});

    template<typename>
    static std::false_type test(...);

public:
    static constexpr bool value = decltype(test<T>(0))::value;
};

TEST(StringTest, SubtractionOperatorIsDeleted) 
{
    static_assert(!has_subtraction<String>::value, "operator- should be deleted");
    SUCCEED();
}

TEST(StringTest, MultiplicationOperatorIsDeleted) 
{
    static_assert(!has_multiplication<String>::value, "operator* should be deleted");
    SUCCEED();
}

TEST(StringTest, DivisionOperatorIsDeleted) 
{
    static_assert(!has_division<String>::value, "operator/ should be deleted");
    SUCCEED();
}