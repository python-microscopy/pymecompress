# PYMECompress

Compression for photon-noise limited images which keeps losses within the Poisson noise envelope

PYMECompress consists of three parts: 

- a fork of the Basic Compression Library originally by Marcus Geelnard, 
modified to include a heavily optimized huffman coder (BCL license is avalable under pymecompress/bcl/doc/manual.pdf and would appear to be BSD compatible)

- a fast, AVX optimized, quantizer to perform "within noise level" quantization of photon-limited images

- a python wrapper of the above. Note that at this point, only huffman coding and quantization are exposed to python

Together they offer a single core throughput of ~500 -600MB/s


## Installation

### Using conda

Prebuilt binaries of PYMEcompress are available as a conda package (*pymecompress*) on the *david_baddeley* conda channel for python 2.7, 3.6 & 3.7, and installable via:

    conda install -c david_baddeley pymecompress

### From source

If you want to modify/contribute to the package you will have to build from source.

Because we use gcc compiler extensions for avx opcodes, we must use gcc/clang for compilation, regardless of platform.

On OSX / linux, a standard `python setup.py install` or `python setup.py develop` should work.

On Windows, you need to install mingw and run the build step first so that you can pass the compiler flag to `python setup.py build` - i.e. :

    python setup.py build --compiler=mingw32
    python setup.py install


A suitable environment for building pymecompress using the following conda command `conda create -n <name> python=x.x numpy cython libpython m2w64-toolchain`

### PIP

Installation via pip is also available:

    pip install pymecompress

however you may need to first set up a build environment (gcc/mingw, as
described for from-source installation) if we have yet to upload a distribution for your platform.
