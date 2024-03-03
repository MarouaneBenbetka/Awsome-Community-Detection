cmake_minimum_required(VERSION 3.19)
project(c__)

set(CMAKE_CXX_STANDARD 14)

include_directories(include)
find_package(Eigen3 REQUIRED)

add_executable(c__
        include/kmeans.hpp
        include/network.hpp
        include/pca.hpp
        src/kmeans.cpp
        src/network.cpp
        src/pca.cpp
        main.cc
        src/utils.cpp
        include/utils.h
        include/utils.h)
