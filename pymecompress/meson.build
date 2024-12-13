#project('pure-and-platlib', 'c', 'cython')

py = import('python').find_installation(pure: false)

np_include_dir = run_command(py,  ['-c',  '"import numpy; print(numpy.get_include())"'], check: true).stdout().strip()

install_dir = py.get_install_dir() / 'pymecompress'

py.extension_module(
  'bcl',
  ['bcl.pyx', 'bcl/huffman.c', 'quantize.c'],
  include_directories: include_directories(np_include_dir),
  #install_dir: install_dir,
  subdir: 'pymecompress',
  install: true,
  #install_rpath: py.get_install_rpath()#,
  #dependencies: py.dependency,
)

# TODO - replace with hard-coded list of sources
#glob = run_command(py, '-c', 'import glob;g = glob.glob("*.py");print("\\n".join(g))', check: true)
#python_sources = glob.stdout().strip().split('\n')
#message(python_sources)

python_sources = [
    '__init__.py',
    'version.py',
    'codecs.py'
]

py.install_sources(python_sources, subdir:'pymecompress')