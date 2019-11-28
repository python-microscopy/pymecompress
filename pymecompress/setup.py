import sys
import os
#import setuptools

if sys.platform == 'darwin':#MacOS
    linkArgs = []
else:
    linkArgs = ['-static-libgcc']


#windows VC++ has really shocking c standard support so we need to include
#custom stdint.h and intypes.h files from https://code.google.com/archive/p/msinttypes
#print os.environ.get('CC', 'foo')
if False: #sys.platform == 'win32' and not os.environ.get('CC', '') == 'mingw':
    extra_include_dirs = ['win_incl']
else:
    extra_include_dirs = []

#import cython_numpy_monkey
#import setuptools

#from Cython.Distutils import build_ext

from Cython.Build import cythonize


#############
# Monkey-patch distutils to not link MSVCR90
import numpy.distutils.mingw32ccompiler
from distutils.unixccompiler import UnixCCompiler
#numpy.distutils.mingw32ccompiler.msvc_runtime_library = lambda : None
numpy.distutils.mingw32ccompiler.build_msvcr_library = lambda debug=False : False

def link(self,
             target_desc,
             objects,
             output_filename,
             output_dir,
             libraries,
             library_dirs,
             runtime_library_dirs,
             export_symbols = None,
             debug=0,
             extra_preargs=None,
             extra_postargs=None,
             build_temp=None,
             target_lang=None):
        # Include the appropiate MSVC runtime library if Python was built
        # with MSVC >= 7.0 (MinGW standard is msvcrt)
        #runtime_library = msvc_runtime_library()
        #if runtime_library:
        #    if not libraries:
        #        libraries = []
        #    libraries.append(runtime_library)
        args = (self,
                target_desc,
                objects,
                output_filename,
                output_dir,
                libraries,
                library_dirs,
                runtime_library_dirs,
                None, #export_symbols, we do this in our def-file
                debug,
                extra_preargs,
                extra_postargs,
                build_temp,
                target_lang)
        if self.gcc_version < "3.0.0":
            func = distutils.cygwinccompiler.CygwinCCompiler.link
        else:
            func = UnixCCompiler.link
        func(*args[:func.__code__.co_argcount])
        return

numpy.distutils.mingw32ccompiler.Mingw32CCompiler.link = link

# End monkey patching
#####################

####
# Python3 windows patch: (here for now to document, should ideally create a better workaround).
# NB - seems to also be needed for recent python 2 (is this a numpy version thing instead?)
#
# modify numpy.distutils.exec_command._exec_command to add line: command[0] = find_executable(command[0])
#

import numpy.distutils.exec_command

def _monkey_patch_exec_command(fcn):
    def _exec_command(command, use_shell=None, use_tee=None, **env):
        command[0] = numpy.distutils.exec_command.find_executable(command[0])
        return fcn(command, use_shell=use_shell, use_tee=use_tee, **env)
        
    return _exec_command
    
if sys.platform == 'win32':
    numpy.distutils.exec_command._exec_command = _monkey_patch_exec_command(numpy.distutils.exec_command._exec_command)

### End exec_command patching

def configuration(parent_package = '', top_path = None):
    from numpy.distutils.misc_util import Configuration, get_numpy_include_dirs
    from numpy.distutils.core import Extension
    from numpy.distutils.misc_util import Configuration, get_numpy_include_dirs
    
    cur_dir = os.path.dirname(__file__)

    if not parent_package == '':
        name = '.'.join([parent_package, 'pymecompress', 'bcl'])
    else:
        name = '.'.join(['pymecompress', 'bcl'])
                        
    
    ext = Extension(name=name,
                    sources=[os.path.join(cur_dir, 'bcl.pyx'), os.path.join(cur_dir, 'bcl/huffman.c'), os.path.join(cur_dir, 'quantize.c')],
                    include_dirs=['bcl',] + get_numpy_include_dirs() + extra_include_dirs,
                    extra_compile_args=['-O3', '-fno-exceptions', '-ffast-math', '-march=native', '-mtune=native'],
                    extra_link_args=linkArgs)

    config = Configuration('pymecompress', parent_package, top_path, ext_modules=cythonize([ext]))
    
    
    # config = Configuration('pymecompress', parent_package, top_path)
    #
    # config.add_extension('bcl',
    #     sources=['bcl.pyx', 'src/huffman.c', 'quantize.c'],
    #     include_dirs = ['src', get_numpy_include_dirs()] + extra_include_dirs,
    # extra_compile_args = ['-O3', '-fno-exceptions', '-ffast-math', '-march=native', '-mtune=native'],
    #     extra_link_args=linkArgs)

    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(description = 'python wrapper for BCL',
        author = 'David Baddeley',
        author_email = 'david.baddeley@yale.edu',
        url = '',
        long_description = """
Python wrapper for the Basic compression libarary
""",
          license = "BSD",
          #cmdclass={'build_ext': build_ext},
          **configuration(top_path='').todict()
          )

