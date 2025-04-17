cmake_minimum_required(VERSION 3.10)
project(harness_libjpeg)

# Utilise Clang si dispo pour support de LibFuzzer
set(CMAKE_C_COMPILER clang)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=fuzzer,address -g")

add_executable(harness_libjpeg harness_libjpeg.c)

# Ajoute la libjpeg installée (tu peux aussi linker une version compilée à la main)
find_library(JPEG_LIB jpeg REQUIRED)
target_link_libraries(harness_libjpeg ${JPEG_LIB})