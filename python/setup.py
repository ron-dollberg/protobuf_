#! /usr/bin/env python
# Protocol Buffers - Google's data interchange format
# Copyright 2008 Google Inc.  All rights reserved.
# https://developers.google.com/protocol-buffers/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# See README for usage instructions.

# pylint:disable=missing-module-docstring
# pylint:disable=g-bad-import-order
from distutils import util
import fnmatch
import glob
import os
import pkg_resources
import re
import subprocess
import sys
import sysconfig

# pylint:disable=g-importing-member
# pylint:disable=g-multiple-import

# We must use setuptools, not distutils, because we need to use the
# namespace_packages option for the "google" package.
from setuptools import setup, Extension, find_packages

from distutils.command.build_ext import build_ext as _build_ext
from distutils.command.build_py import build_py as _build_py
from distutils.command.clean import clean as _clean
from distutils.spawn import find_executable

# Find the Protocol Compiler.
if 'PROTOC' in os.environ and os.path.exists(os.environ['PROTOC']):
  protoc = os.environ['PROTOC']
elif os.path.exists('../bazel-bin/protoc'):
  protoc = '../bazel-bin/protoc'
elif os.path.exists('../bazel-bin/protoc.exe'):
  protoc = '../bazel-bin/protoc.exe'
elif os.path.exists('protoc'):
  protoc = '../protoc'
elif os.path.exists('protoc.exe'):
  protoc = '../protoc.exe'
elif os.path.exists('../vsprojects/Debug/protoc.exe'):
  protoc = '../vsprojects/Debug/protoc.exe'
elif os.path.exists('../vsprojects/Release/protoc.exe'):
  protoc = '../vsprojects/Release/protoc.exe'
else:
  protoc = find_executable('protoc')


def GetVersion():
  """Reads and returns the version from google/protobuf/__init__.py.

  Do not import google.protobuf.__init__ directly, because an installed
  protobuf library may be loaded instead.

  Returns:
      The version.
  """

  with open(os.path.join('_google', 'protobuf', '__init__.py')) as version_file:
    exec(version_file.read(), globals())  # pylint:disable=exec-used
    return __version__  # pylint:disable=undefined-variable


def GenProto(source, require=True):
  """Generates a _pb2.py from the given .proto file.

  Does nothing if the output already exists and is newer than the input.

  Args:
      source: the .proto file path.
      require: if True, exit immediately when a path is not found.
  """

  if not require and not os.path.exists(source):
    return

  output = source.replace('.proto', '_pb2.py').replace('../src/', '')

  if (not os.path.exists(output) or
      (os.path.exists(source) and
       os.path.getmtime(source) > os.path.getmtime(output))):
    print('Generating %s...' % output)

    if not os.path.exists(source):
      sys.stderr.write("Can't find required file: %s\n" % source)
      sys.exit(-1)

    if protoc is None:
      sys.stderr.write(
          'protoc is not installed nor found in ../src.  Please compile it '
          'or install the binary package.\n')
      sys.exit(-1)

    protoc_command = [protoc, '-I../src', '-I.', '--python_out=.', source]
    if subprocess.call(protoc_command) != 0:
      sys.exit(-1)


def GenerateUnittestProtos():
  """Generates protobuf code for unittests."""
  GenProto('../src/google/protobuf/any_test.proto', False)
  GenProto('../src/google/protobuf/map_proto2_unittest.proto', False)
  GenProto('../src/google/protobuf/map_unittest.proto', False)
  GenProto('../src/google/protobuf/test_messages_proto3.proto', False)
  GenProto('../src/google/protobuf/test_messages_proto2.proto', False)
  GenProto('../src/google/protobuf/unittest_arena.proto', False)
  GenProto('../src/google/protobuf/unittest.proto', False)
  GenProto('../src/google/protobuf/unittest_custom_options.proto', False)
  GenProto('../src/google/protobuf/unittest_import.proto', False)
  GenProto('../src/google/protobuf/unittest_import_public.proto', False)
  GenProto('../src/google/protobuf/unittest_mset.proto', False)
  GenProto('../src/google/protobuf/unittest_mset_wire_format.proto', False)
  GenProto('../src/google/protobuf/unittest_no_generic_services.proto', False)
  GenProto('../src/google/protobuf/unittest_proto3_arena.proto', False)
  GenProto('../src/google/protobuf/util/json_format.proto', False)
  GenProto('../src/google/protobuf/util/json_format_proto3.proto', False)
  GenProto('_google/protobuf/internal/any_test.proto', False)
  GenProto('_google/protobuf/internal/descriptor_pool_test1.proto', False)
  GenProto('_google/protobuf/internal/descriptor_pool_test2.proto', False)
  GenProto('_google/protobuf/internal/factory_test1.proto', False)
  GenProto('_google/protobuf/internal/factory_test2.proto', False)
  GenProto('_google/protobuf/internal/file_options_test.proto', False)
  GenProto('_google/protobuf/internal/import_test_package/import_public.proto',
           False)
  GenProto(
      '_google/protobuf/internal/import_test_package/import_public_nested.proto',
      False)
  GenProto('_google/protobuf/internal/import_test_package/inner.proto', False)
  GenProto('_google/protobuf/internal/import_test_package/outer.proto', False)
  GenProto('_google/protobuf/internal/missing_enum_values.proto', False)
  GenProto('_google/protobuf/internal/message_set_extensions.proto', False)
  GenProto('_google/protobuf/internal/more_extensions.proto', False)
  GenProto('_google/protobuf/internal/more_extensions_dynamic.proto', False)
  GenProto('_google/protobuf/internal/more_messages.proto', False)
  GenProto('_google/protobuf/internal/no_package.proto', False)
  GenProto('_google/protobuf/internal/packed_field_test.proto', False)
  GenProto('_google/protobuf/internal/test_bad_identifiers.proto', False)
  GenProto('_google/protobuf/internal/test_proto3_optional.proto', False)
  GenProto('_google/protobuf/pyext/python.proto', False)


class CleanCmd(_clean):
  """Custom clean command for building the protobuf extension."""

  def run(self):
    # Delete generated files in the code tree.
    for (dirpath, unused_dirnames, filenames) in os.walk('.'):
      for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        if (filepath.endswith('_pb2.py') or filepath.endswith('.pyc') or
            filepath.endswith('.so') or filepath.endswith('.o')):
          os.remove(filepath)
    # _clean is an old-style class, so super() doesn't work.
    _clean.run(self)


class BuildPyCmd(_build_py):
  """Custom build_py command for building the protobuf runtime."""

  def run(self):
    # Generate necessary .proto file if it doesn't exist.
    GenProto('../src/google/protobuf/descriptor.proto')
    GenProto('../src/google/protobuf/compiler/plugin.proto')
    GenProto('../src/google/protobuf/any.proto')
    GenProto('../src/google/protobuf/api.proto')
    GenProto('../src/google/protobuf/duration.proto')
    GenProto('../src/google/protobuf/empty.proto')
    GenProto('../src/google/protobuf/field_mask.proto')
    GenProto('../src/google/protobuf/source_context.proto')
    GenProto('../src/google/protobuf/struct.proto')
    GenProto('../src/google/protobuf/timestamp.proto')
    GenProto('../src/google/protobuf/type.proto')
    GenProto('../src/google/protobuf/wrappers.proto')
    GenerateUnittestProtos()

    # _build_py is an old-style class, so super() doesn't work.
    _build_py.run(self)

  def find_package_modules(self, package, package_dir):
    exclude = (
        '*test*',
        '_google/protobuf/internal/*_pb2.py',
        '_google/protobuf/internal/_parameterized.py',
        '_google/protobuf/pyext/python_pb2.py',
    )
    modules = _build_py.find_package_modules(self, package, package_dir)
    return [(pkg, mod, fil) for (pkg, mod, fil) in modules
            if not any(fnmatch.fnmatchcase(fil, pat=pat) for pat in exclude)]


class BuildExtCmd(_build_ext):
  """Command class for building the protobuf Python extension."""

  def get_ext_filename(self, ext_name):
    # since python3.5, python extensions' shared libraries use a suffix that
    # corresponds to the value of sysconfig.get_config_var('EXT_SUFFIX') and
    # contains info about the architecture the library targets.  E.g. on x64
    # linux the suffix is ".cpython-XYZ-x86_64-linux-gnu.so" When
    # crosscompiling python wheels, we need to be able to override this
    # suffix so that the resulting file name matches the target architecture
    # and we end up with a well-formed wheel.
    filename = _build_ext.get_ext_filename(self, ext_name)
    orig_ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
    new_ext_suffix = os.getenv('PROTOCOL_BUFFERS_OVERRIDE_EXT_SUFFIX')
    if new_ext_suffix and filename.endswith(orig_ext_suffix):
      filename = filename[:-len(orig_ext_suffix)] + new_ext_suffix
    return filename


class TestConformanceCmd(_build_py):
  target = '//python:conformance_test'

  def run(self):
    # Python 2.6 dodges these extra failures.
    os.environ['CONFORMANCE_PYTHON_EXTRA_FAILURES'] = (
        '--failure_list failure_list_python-post26.txt')
    cmd = 'bazel test %s' % (TestConformanceCmd.target,)
    subprocess.check_call(cmd, shell=True)


def GetOptionFromArgv(option_str):
  if option_str in sys.argv:
    sys.argv.remove(option_str)
    return True
  return False


def _GetFlagValues(flag_long, flag_short):
  """Searches sys.argv for distutils-style flags and yields values."""

  expect_value = flag_long.endswith('=')
  flag_res = [re.compile(r'--?%s(=(.*))?' %
                         (flag_long[:-1] if expect_value else flag_long))]
  if flag_short:
    flag_res.append(re.compile(r'-%s(.*)?' % (flag_short,)))

  flag_match = None
  for arg in sys.argv:
    # If the last arg was like '-O', check if this is the library we want.
    if flag_match is not None:
      yield arg
      flag_match = None
      continue

    for flag_re in flag_res:
      m = flag_re.match(arg)
      if m is None:
        continue
      if not expect_value:
        yield arg
        continue
      groups = m.groups()
      # Check for matches:
      #   --long-name=foo => ('=foo', 'foo')
      #   -Xfoo => ('foo')
      # N.B.: if the flag is like '--long-name=', then there is a value
      # (the empty string).
      if groups[0] or groups[-1]:
        yield groups[-1]
        continue
      flag_match = m

  return False


def HasStaticLibprotobufOpt():
  """Returns true if there is a --link-objects arg for libprotobuf."""

  lib_re = re.compile(r'(.*[/\\])?(lib)?protobuf([.]pic)?[.](a|lib)')
  for value in _GetFlagValues('link-objects=', 'O'):
    if lib_re.match(value):
      return True
  return False


def HasLibraryDirsOpt():
  """Returns true if there is a --library-dirs arg."""
  return any(_GetFlagValues('library-dirs=', 'L'))


if __name__ == '__main__':
  ext_module_list = []
  warnings_as_errors = '--warnings_as_errors'
  if GetOptionFromArgv('--cpp_implementation'):
    # Link libprotobuf.a and libprotobuf-lite.a statically with the
    # extension. Note that those libraries have to be compiled with
    # -fPIC for this to work.
    compile_static_ext = HasStaticLibprotobufOpt()
    if GetOptionFromArgv('--compile_static_extension'):
      # FUTURE: add a warning and deprecate --compile_static_extension.
      compile_static_ext = True
    extra_objects = None
    if compile_static_ext:
      libraries = None
      library_dirs = None
      if not HasStaticLibprotobufOpt():
        if os.path.exists('../bazel-bin/src/google/protobuf/libprotobuf.a'):
          extra_objects = ['../bazel-bin/src/google/protobuf/libprotobuf.a']
        else:
          extra_objects = ['../libprotobuf.a']
          extra_objects += list(
              glob.iglob('../third_party/utf8_range/*.a'))
          # Repeat all of these enough times to eliminate order-dependence.
          extra_objects += list(
              glob.iglob('../third_party/abseil-cpp/absl/**/*.a'))
          extra_objects += list(
              glob.iglob('../third_party/abseil-cpp/absl/**/*.a'))
          extra_objects += list(
              glob.iglob('../third_party/abseil-cpp/absl/**/*.a'))
    else:
      libraries = ['protobuf']
      if HasLibraryDirsOpt():
        library_dirs = None
      elif os.path.exists('../bazel-bin/src/google/protobuf/libprotobuf.a'):
        library_dirs = ['../bazel-bin/src/google/protobuf']
      else:
        library_dirs = ['..']

    TestConformanceCmd.target = ('//python:conformance_test_cpp '
                                 '--define=use_fast_cpp_protos=true')

    extra_compile_args = []

    message_extra_link_args = None
    api_implementation_link_args = None
    if 'darwin' in sys.platform:
      if sys.version_info[0] == 2:
        message_init_symbol = 'init_message'
        api_implementation_init_symbol = 'init_api_implementation'
      else:
        message_init_symbol = 'PyInit__message'
        api_implementation_init_symbol = 'PyInit__api_implementation'
      message_extra_link_args = [
          '-Wl,-exported_symbol,_%s' % message_init_symbol
      ]
      api_implementation_link_args = [
          '-Wl,-exported_symbol,_%s' % api_implementation_init_symbol
      ]

    if sys.platform != 'win32':
      extra_compile_args.append('-Wno-write-strings')
      extra_compile_args.append('-Wno-invalid-offsetof')
      extra_compile_args.append('-Wno-sign-compare')
      extra_compile_args.append('-Wno-unused-variable')
      extra_compile_args.append('-std=c++14')

    if sys.platform == 'darwin':
      extra_compile_args.append('-Wno-shorten-64-to-32')
      extra_compile_args.append('-Wno-deprecated-register')

    # https://developer.apple.com/documentation/xcode_release_notes/xcode_10_release_notes
    # C++ projects must now migrate to libc++ and are recommended to set a
    # deployment target of macOS 10.9 or later, or iOS 7 or later.
    if sys.platform == 'darwin':
      mac_target = str(sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET'))
      if mac_target and (pkg_resources.parse_version(mac_target) <
                         pkg_resources.parse_version('10.9.0')):
        os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'
        os.environ['_PYTHON_HOST_PLATFORM'] = re.sub(
            r'macosx-[0-9]+\.[0-9]+-(.+)', r'macosx-10.9-\1',
            util.get_platform())

    # https://github.com/Theano/Theano/issues/4926
    if sys.platform == 'win32':
      extra_compile_args.append('-D_hypot=hypot')

    # https://github.com/tpaviot/pythonocc-core/issues/48
    if sys.platform == 'win32' and  '64 bit' in sys.version:
      extra_compile_args.append('-DMS_WIN64')

    # MSVS default is dymanic
    if sys.platform == 'win32':
      extra_compile_args.append('/MT')

    if 'clang' in os.popen('$CC --version 2> /dev/null').read():
      extra_compile_args.append('-Wno-shorten-64-to-32')

    if warnings_as_errors in sys.argv:
      extra_compile_args.append('-Werror')
      sys.argv.remove(warnings_as_errors)

    # C++ implementation extension
    ext_module_list.extend([
        Extension(
            '_google.protobuf.pyext._message',
            glob.glob('_google/protobuf/pyext/*.cc'),
            include_dirs=['.', '../src', '../third_party/abseil-cpp'],
            libraries=libraries,
            extra_objects=extra_objects,
            extra_link_args=message_extra_link_args,
            library_dirs=library_dirs,
            extra_compile_args=extra_compile_args,
        ),
        Extension(
            '_google.protobuf.internal._api_implementation',
            glob.glob('_google/protobuf/internal/api_implementation.cc'),
            extra_compile_args=(extra_compile_args +
                                ['-DPYTHON_PROTO2_CPP_IMPL_V2']),
            extra_link_args=api_implementation_link_args,
        ),
    ])
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'cpp'

  # Keep this list of dependencies in sync with tox.ini.
  install_requires = []

  setup(
      name='protobuff',
      version=GetVersion(),
      description='Protocol Buffers',
      download_url='https://github.com/protocolbuffers/protobuf/releases',
      long_description="Protocol Buffers are Google's data interchange format",
      url='https://developers.google.com/protocol-buffers/',
      project_urls={
          'Source': 'https://github.com/protocolbuffers/protobuf',
      },
      maintainer='protobuf@googlegroups.com',
      maintainer_email='protobuf@googlegroups.com',
      license='BSD-3-Clause',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
      ],
      namespace_packages=['_google'],
      packages=find_packages(
          exclude=[
              'import_test_package',
              'protobufdistutils',
          ],),
      test_suite='_google.protobuf.internal',
      cmdclass={
          'clean': CleanCmd,
          'build_py': BuildPyCmd,
          'build_ext': BuildExtCmd,
          'test_conformance': TestConformanceCmd,
      },
      install_requires=install_requires,
      ext_modules=ext_module_list,
      python_requires='>=3.7',
  )
