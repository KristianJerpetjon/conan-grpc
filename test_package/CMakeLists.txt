cmake_minimum_required(VERSION 2.8.12)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(NOT MSVC)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
else()
  add_definitions(-D_WIN32_WINNT=0x600)
endif()

#find grpc
find_package(gRPC CONFIG REQUIRED)
#find protoc
find_package(Protobuf CONFIG REQUIRED)

message(STATUS "Using protobuf ${protobuf_VERSION}")
message(STATUS "Using gRPC ${gRPC_VERSION}")

set(PROTOS helloworld.proto)
include_directories(${CMAKE_CURRENT_BINARY_DIR})

#generate protobuf stuff
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTOS})
#generate grpc stuff
grpc_generate_cpp(GRPC_SRCS GRPC_HDRS ${CMAKE_CURRENT_BINARY_DIR} ${PROTOS})

# Targets greeter_[async_](client)
foreach(_target
  greeter_client)
# greeter_server greeter_async_client greeter_async_server)
  add_executable(${_target} "${_target}.cc"
    ${PROTO_SRCS}
    ${GRPC_SRCS})
  target_link_libraries(${_target}
    CONAN_PKG::protobuf
    CONAN_PKG::grpc
  )
endforeach()
