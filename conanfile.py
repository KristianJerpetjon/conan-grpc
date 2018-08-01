from conans import ConanFile, CMake, tools
import os


class grpcConan(ConanFile):
    name = "grpc"
    version = "1.14.0-pre2"
    description = "Google's RPC library and framework."
    url = "https://github.com/inexorgame/conan-grpc"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"
    requires = "zlib/1.2.11@conan/stable", "OpenSSL/1.0.2o@conan/stable", "protobuf/3.5.2@bincrafters/stable", "gflags/2.2.1@bincrafters/stable", "c-ares/1.14.0@conan/stable", "google_benchmark/1.4.1@inexorgame/stable"
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            # "enable_mobile": [True, False],  # Enables iOS and Android support
            # "non_cpp_plugins": [True, False],  # Enables plugins such as --java-out and --py-out (if False, only --cpp-out is possible)
            "build_csharp_ext": [True, False],
            "build_codegen": [True, False]
            }
    default_options = '''shared=False
    build_codegen=True
    build_csharp_ext=False
    fPIC=True
    '''
    # enable_mobile=False
    # non_cpp_plugins=False

    exports_sources = "CMakeLists.txt",
    generators = "cmake"
    short_paths = True  # Otherwise some folders go out of the 260 chars path length scope rapidly (on windows)

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def source(self):
        archive_url = "https://github.com/grpc/grpc/archive/v{}.zip".format(self.version)
        tools.get(archive_url, sha256="a43d9e27c571ba226ae9275cb3658f3009fbe7a9f8e622f72cca347e1c104440")
        os.rename("grpc-{!s}".format(self.version), self.source_subfolder)

        # cmake_name = "{}/CMakeLists.txt".format(self.source_subfolder)

        # Add some CMake Variables (effectively commenting out stuff we do not support)
        # tools.replace_in_file(cmake_name, "add_library(grpc_cronet", '''if(CONAN_ENABLE_MOBILE)
        # add_library(grpc_cronet''')
        # tools.replace_in_file(cmake_name, "add_library(grpc_unsecure", '''endif(CONAN_ENABLE_MOBILE)
        # add_library(grpc_unsecure''')
        # tools.replace_in_file(cmake_name, "add_library(grpc++_cronet", '''if(CONAN_ENABLE_MOBILE)
        # add_library(grpc++_cronet''')
        # tools.replace_in_file(cmake_name, "add_library(grpc++_reflection", '''endif(CONAN_ENABLE_MOBILE)
        # if(CONAN_ENABLE_REFLECTION_LIBS)
        # add_library(grpc++_reflection''')
        # tools.replace_in_file(cmake_name, "add_library(grpc++_unsecure", '''endif(CONAN_ENABLE_REFLECTION_LIBS)
        # add_library(grpc++_unsecure''')
        # # tools.replace_in_file(cmake_name, "add_executable(gen_hpack_tables", '''endif(CONAN_ADDITIONAL_PLUGINS)
        # tools.replace_in_file(cmake_name, "add_executable(gen_hpack_tables", '''
        # if(CONAN_ADDITIONAL_BINS)
        # add_executable(gen_hpack_tables''')
        # tools.replace_in_file(cmake_name, "add_executable(gen_legal_metadata_characters", '''endif(CONAN_ADDITIONAL_BINS)
        # add_executable(gen_legal_metadata_characters''')
        # tools.replace_in_file(cmake_name, "add_executable(grpc_csharp_plugin", '''if(CONAN_ADDITIONAL_PLUGINS)
        # add_executable(grpc_csharp_plugin''')
        #
        # tools.replace_in_file(cmake_name, '''  install(TARGETS grpc_ruby_plugin EXPORT gRPCTargets{0!s}    RUNTIME DESTINATION ${{gRPC_INSTALL_BINDIR}}{0!s}    LIBRARY DESTINATION ${{gRPC_INSTALL_LIBDIR}}{0!s}    ARCHIVE DESTINATION ${{gRPC_INSTALL_LIBDIR}}{0!s}  ){0!s}endif()'''.format('\n'), '''  install(TARGETS grpc_ruby_plugin EXPORT gRPCTargets{0!s}    RUNTIME DESTINATION ${{gRPC_INSTALL_BINDIR}}{0!s}    LIBRARY DESTINATION ${{gRPC_INSTALL_LIBDIR}}{0!s}    ARCHIVE DESTINATION ${{gRPC_INSTALL_LIBDIR}}{0!s}  ){0!s}endif(){0!s}endif(CONAN_ADDITIONAL_PLUGINS)'''.format('\n'))

    def _configure_cmake(self):
        cmake = CMake(self)

        # This doesn't work yet as one would expect, because the install target builds everything
        # and we need the install target because of the generated CMake files
        # if self.options.non_cpp_plugins:
        #     cmake.definitions['CONAN_ADDITIONAL_PLUGINS'] = "ON"
        # else:
        #     cmake.definitions['CONAN_ADDITIONAL_PLUGINS'] = "OFF"
        #
        # # Doesn't work yet for the same reason as above
        # if self.options.enable_mobile:
        #     cmake.definitions['CONAN_ENABLE_MOBILE'] = "ON"

        cmake.definitions['gRPC_BUILD_CSHARP_EXT'] = "ON" if self.options.build_csharp_ext else "OFF"
        cmake.definitions['gRPC_BUILD_CODEGEN'] = "ON" if self.options.build_codegen else "OFF"


        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        cmake.definitions['gRPC_INSTALL'] = "ON"
        # cmake.definitions['CMAKE_INSTALL_PREFIX'] = self.build_subfolder

        # tell grpc to use the find_package versions
        cmake.definitions['gRPC_CARES_PROVIDER'] = "package"
        cmake.definitions['gRPC_ZLIB_PROVIDER'] = "package"
        cmake.definitions['gRPC_SSL_PROVIDER'] = "package"
        cmake.definitions['gRPC_PROTOBUF_PROVIDER'] = "package"
        cmake.definitions['gRPC_GFLAGS_PROVIDER'] = "package"
        cmake.definitions['gRPC_BENCHMARK_PROVIDER'] = "package"

        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('*', dst='include', src='{}/include'.format(self.source_subfolder))
        self.copy('*.cmake', dst='lib', src='{}/lib'.format(self.build_subfolder), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        self.copy("*", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["grpc", "grpc++", "grpc_unsecure", "grpc++_unsecure", "gpr"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs += ["wsock32", "ws2_32"]
