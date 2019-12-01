# PYMECompress

PYMECompress consists of three parts: 

- a fork of the Basic Compression Library originally by Marcus Geelnard, 
modified to include a heavily optimized huffman coder (BCL license is avalable under pymecompress/bcl/doc/manual.pdf and would appear to be BSD compatible)

- a fast, AVX optimized, quantizer to perform "within noise level" quantization of photon-limited images

- a python wrapper of the above. Note that at this point, only huffman coding and quantization are exposed to python

Together they offer a single core throughput of ~500 -600MB/s


## Installation

PYMEcompress is available as a conda package ("pymecompress") on the "david_baddeley" conda channel for python 2.7, 3.6 & 3.7
    
Because we use gcc compiler extensions for avx opcodes, we must use gcc/clang for compilation, regardless of platform.
On OSX / linux, a standard `python setup.py install` or `python setup.py develop` should work.

On Windows, you need to build first - i.e. :

    cd pymecompress
    python setup.py build --compiler=mingw32
    python setup.py install

