cmake_minimum_required(VERSION 3.10)
project(AlgEdu)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CONFIGURATION_TYPES "Debug;Release;Test" CACHE STRING "Configurations" FORCE)
if(MSVC)
    set(CMAKE_CXX_FLAGS_DEBUG "/DEBUG /Od /DDEBUG")
    set(CMAKE_CXX_FLAGS_RELEASE "/O2 /DNDEBUG")
    set(CMAKE_CXX_FLAGS_TEST "/DEBUG /O1 /DTEST")
else()
    set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -DDEBUG")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
    set(CMAKE_CXX_FLAGS_TEST "-g -O1 -DTEST")
endif()

set(SOURCES
    desktop/source/assignment.cpp
    desktop/source/baseStatement.cpp
    desktop/source/baseVariable.cpp
    desktop/source/declaration.cpp
    desktop/source/integer.cpp
    desktop/source/lexer.cpp
    desktop/source/main.cpp
    desktop/source/parser.cpp
    desktop/source/string.cpp
    desktop/source/token.cpp
)

set(HEADERS
    desktop/source/assignment.h
    desktop/source/baseStatement.h
    desktop/source/baseVariable.h
    desktop/source/declaration.h
    desktop/source/integer.h
    desktop/source/lexer.h
    desktop/source/main.h
    desktop/source/parser.h
    desktop/source/string.h
    desktop/source/token.h
    desktop/source/tokenType.h
    desktop/source/standardStatements.h
)

add_executable(AlgEdu ${SOURCES})

target_include_directories(AlgEdu PRIVATE 
    desktop/source
    desktop/vendor/imgui-docking
)

file(GLOB IMGUI_SOURCES 
    "desktop/vendor/imgui-docking/*.cpp"
    "desktop/vendor/imgui-docking/backends/imgui_impl_dx12.cpp"
    "desktop/vendor/imgui-docking/backends/imgui_impl_dx12.h"
    "desktop/vendor/imgui-docking/backends/imgui_impl_win32.cpp"
    "desktop/vendor/imgui-docking/backends/imgui_impl_win32.h"
)

add_library(imgui STATIC ${IMGUI_SOURCES})
target_include_directories(imgui PUBLIC 
    desktop/vendor/imgui-docking
    desktop/vendor/imgui-docking/backends
)

find_package(Boost REQUIRED COMPONENTS filesystem system)

target_link_libraries(AlgEdu PRIVATE 
    imgui
    Boost::filesystem 
    Boost::system
)

enable_testing()

file(GLOB TEST_SOURCES "test/*.cpp")

if(TEST_SOURCES)
    add_executable(AlgEduTests ${TEST_SOURCES} ${SOURCES})
    
    target_include_directories(AlgEduTests PRIVATE
        desktop/source
        ${CMAKE_CURRENT_SOURCE_DIR}/test
    )
    
    add_subdirectory(desktop/vendor/googletest)
    target_link_libraries(AlgEduTests PRIVATE
        imgui
        Boost::filesystem
        Boost::system
        gtest_main
    )
    
    add_test(NAME AlgEduTests COMMAND AlgEduTests)
endif()