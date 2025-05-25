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
    desktop/source/baseVariable.cpp
    desktop/source/baseStatement.cpp
    desktop/source/cell.cpp
    desktop/source/cellCord.cpp
    desktop/source/declaration.cpp
    desktop/source/integer.cpp
    desktop/source/lexer.cpp
    desktop/source/main.cpp
    desktop/source/parser.cpp
    desktop/source/string.cpp
    desktop/source/token.cpp
)

set(HEADERS
    desktop/include/assignment.h
    desktop/include/baseStatement.h
    desktop/include/baseVariable.h
    desktop/include/cell.h
    desktop/include/cellCord.h
    desktop/include/commandType.h
    desktop/include/declaration.h
    desktop/include/frameContext.h
    desktop/include/gridCommand.h
    desktop/include/integer.h
    desktop/include/lexer.h
    desktop/include/parser.h
    desktop/include/standardStatements.h
    desktop/include/string.h
    desktop/include/token.h
    desktop/include/tokenType.h
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
