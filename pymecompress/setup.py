import sys
import os
#import setuptools

linkArgs = []
if sys.platform == 'win32':
    linkArgs = ['-static-libgcc']
    
    #if sys.version_info[0] == 3:
    #    linkArgs.append('-l python3.lib')


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
            import distutils
            func = distutils.cygwinccompiler.CygwinCCompiler.link
        else:
            func = UnixCCompiler.link
        func(*args[:func.__code__.co_argcount])
        return

numpy.distutils.mingw32ccompiler.Mingw32CCompiler.link = link



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
import subprocess
from numpy.distutils.exec_command import find_executable

#objdump is a .bat rather than a .exe in an anaconda build environment
def _monkey_patch_dump_table(dll):
    objdump = find_executable("objdump")
    st = subprocess.Popen([objdump, "-p", dll], stdout=subprocess.PIPE)
    return st.stdout.readlines()

numpy.distutils.mingw32ccompiler.dump_table = _monkey_patch_dump_table

# ditto for dlltool
def _build_import_library_amd64():
    out_exists, out_file = numpy.distutils.mingw32ccompiler._check_for_import_lib()
    if out_exists:
        numpy.distutils.mingw32ccompiler.log.debug('Skip building import library: "%s" exists', out_file)
        return

    # get the runtime dll for which we are building import library
    dll_file = numpy.distutils.mingw32ccompiler.find_python_dll()
    numpy.distutils.mingw32ccompiler.log.info('Building import library (arch=AMD64): "%s" (from %s)' %
             (out_file, dll_file))

    # generate symbol list from this library
    def_name = "python%d%d.def" % tuple(sys.version_info[:2])
    def_file = os.path.join(sys.prefix, 'libs', def_name)
    numpy.distutils.mingw32ccompiler.generate_def(dll_file, def_file)

    # generate import library from this symbol list
    cmd = [find_executable("dlltool"), '-d', def_file, '-l', out_file]
    subprocess.Popen(cmd)

numpy.distutils.mingw32ccompiler._build_import_library_amd64 = _build_import_library_amd64

# End monkey patching
#####################

#pre-compile cython (copied & adapted from skimage._build)
def cython(pyx_files, working_path=''):
    """Use Cython to convert the given files to C.
    Parameters
    ----------
    pyx_files : list of str
        The input .pyx files.
    """
    # Do not build cython files if target is clean
    if len(sys.argv) >= 2 and sys.argv[1] == 'clean':
        return

    try:

        from Cython.Build import cythonize
    except ImportError:
        # If cython is not found, the build will make use of
        # the distributed .c or .cpp files if present
       

        print("Cython not found; falling back to pre-built bcl.c")
    else:
        from multiprocessing import cpu_count
        pyx_files = [os.path.join(working_path, f) for f in pyx_files]

        # Cython doesn't automatically choose a number of threads > 1
        # https://github.com/cython/cython/blob/a0bbb940c847dfe92cac446c8784c34c28c92836/Cython/Build/Dependencies.py#L923-L925
        cythonize(pyx_files, nthreads=cpu_count(),
                  compiler_directives={'language_level': sys.version_info.major})

def configuration(parent_package = '', top_path = None):
    from numpy.distutils.core import Extension
    from numpy.distutils.misc_util import Configuration, get_numpy_include_dirs

    if not parent_package == '':
        name = '.'.join([parent_package, 'pymecompress', 'bcl'])
    else:
        name = '.'.join(['pymecompress', 'bcl'])
    
    #cythonize pyx files
    cython(['bcl.pyx',], working_path=os.path.abspath(os.path.dirname(__file__)))

    config = Configuration('pymecompress', parent_package, top_path)
    config.get_version()
    
    config.add_extension(name='bcl',
                    #sources=[os.path.join(cur_dir, 'bcl.pyx'), os.path.join(cur_dir, 'bcl/huffman.c'), os.path.join(cur_dir, 'quantize.c')],
                    sources=['bcl.c', 'bcl/huffman.c','quantize.dispatch.c', 'quantize.c'],
                    include_dirs=['bcl',] + get_numpy_include_dirs() + extra_include_dirs,
                    extra_compile_args=['-O3', '-fno-exceptions', '-ffast-math',],
                    extra_link_args=linkArgs)

    

    return config


# import distutils
# class build_ext_subclass(distutils.command.build_ext.build_ext):
#     def build_extensions(self):

#         original__compile = self.compiler._compile
#         def new__compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
#             if src.endswith("_AVX.c"):
#                 extra_postargs = extra_postargs + ['-mavx',]
#             return original__compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
#         self.compiler._compile = new__compile
#         try:
#             distutils.command.build_ext.build_ext.build_extensions(self)
#         finally:
#             del self.compiler._compile

if __name__ == '__main__':
    from numpy.distutils.core import setup
    
    setup(description = 'Compression for photon-noise limited images which keeps losses within the Poisson noise envelope',
          author = 'David Baddeley',
          author_email = 'david.baddeley@yale.edu',
          url = 'https://github.com/python-microscopy/pymecompress',
          long_description = 'Compression for photon-noise limited images which keeps losses within the Poisson noise envelope',
          license = "BSD",
          install_requires=['numpy'],
          classifiers=[
              'Development Status :: 3 - Alpha',
              # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
              'License :: OSI Approved :: BSD License', # Again, pick a license
              'Programming Language :: Python :: 2.7', #Specify which pyhton versions that you want to support
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3.7',
          ],
          **configuration(top_path='').todict()
         )

