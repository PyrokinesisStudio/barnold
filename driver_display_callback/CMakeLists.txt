cmake_minimum_required(VERSION 3.5)
project(barnold_display_callback)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)
include(CheckCXXCompilerFlag)
enable_testing()
#set(CMAKE_BUILD_TYPE DEBUG)
set(CMAKE_BUILD_TYPE RELEASE)

set(SOURCE_FILES
    src/driver_display_callback.cpp
    )

# Sorry, this is hardcoded
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules/")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -fPIC -Wno-narrowing")

find_package(Arnold REQUIRED)
set(CMAKE_INSTALL_RPATH "$ENV{ARNOLD_HOME}/bin")
get_filename_component(ArnLib ${ARNOLD_LIBRARIES} DIRECTORY )
message(${ArnLib})

include_directories(${ARNOLD_INCLUDE_DIRS})
link_directories(${ArnLib})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${ARNOLD_LIBRARIES})

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/../bin" CACHE PATH "Default install path" FORCE)
endif()

install(TARGETS ${PROJECT_NAME}
        DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/../bin"
        # DESTINATION "${CMAKE_INSTALL_PREFIX}/python/RS_Blender"
        # DESTINATION "${ARNOLD_HOME}/plugins"

)
