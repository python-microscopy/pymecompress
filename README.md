# PYMECompress
![testing](https://github.com/python-microscocopy/pymecompress/actions/workflows/test.yml/badge.svg)
![conda](https://img.shields.io/conda/v/david_baddeley/pymecompress)
![pypi](https://img.shields.io/pypi/v/pymecompress)
![pyversions](https://img.shields.io/pypi/pyversions/pymecompress)

Compression for photon-noise limited images which keeps losses within the Poisson noise envelope

PYMECompress consists of four parts: 

- a fork of the Basic Compression Library originally by Marcus Geelnard, 
modified to include a heavily optimized huffman coder (BCL license is avalable under pymecompress/bcl/doc/manual.pdf and would appear to be BSD compatible)

- a fast, AVX optimized, quantizer to perform "within noise level" quantization of photon-limited images

- a python wrapper of the above. Note that at this point, only huffman coding and quantization are exposed to python

- numcodecs codecs (experimental) to permit simple usage with other IO packages - e.g. Zarr

Together they offer a single core throughput of ~500 -600MB/s


## Installation

### conda

Prebuilt binaries of PYMEcompress are available as a conda package (*pymecompress*) on the *david_baddeley* conda channel for python 2.7, 3.6 & 3.7, and installable via:

    conda install -c david_baddeley pymecompress

### source

If you want to modify/contribute to the package you will have to build from source.

Because we use gcc compiler extensions for avx opcodes, we must use gcc/clang for compilation, regardless of platform.

On OSX / linux, a standard `python setup.py install` or `python setup.py develop` should work.

On Windows, you need to install mingw and run the build step first so that you can pass the compiler flag to `python setup.py build` - i.e. :

    python setup.py build --compiler=mingw32
    python setup.py install


A suitable environment for building pymecompress can be created using the following conda command `conda create -n <name> python=x.x numpy cython libpython m2w64-toolchain`

### pip

Installation via pip is also available:

    pip install pymecompress

although binary wheels are not available for all platforms so you may need to set up a build environment (gcc/mingw, as described for source installation) first.

## Usage

### numcodecs codecs

```python
import numpy as np
from pymecompress import codecs

# vanilla huffman coding (lossless). NB - input buffer must be bytes/uint8
huff = codecs.Huffman()
d = np.ones(1000)
assert np.allclose(huff.decode(huff.encode(d.view('uint8'))).view(d.dtype), d)


# with quantisation NB: input data type MUST be uint16
huffq = codecs.HuffmanQuant16(offset=0, scale=1.0)
ds = np.linspace(1,2**15).astype('uint16')

assert np.all((huffq.decode(huffq.encode(ds)) - ds.astype('f')) < np.sqrt(ds))

```

### As a Zarr compression filter

VERY EXPERIMENTAL! 

This is not yet well tested, but should work as described in https://zarr.readthedocs.io/en/stable/api/codecs.html. In brief ...

```python
import zarr
from pymecompress import codecs
z = zarr.zeros(1000000, dtype='uint16', compressor=codecs.HuffmanQuant16(offset=0, scale=1))

```

**NB** To be able to read/open files saved using the pymecompress codecs you will probably need to run `from pymecompress import codecs`
to register the codecs with `numcodecs` before trying to open the file.

### Directly calling functions

As you need to supply the original size to the decompression function, these are most suitable when putting the compressed data in an external wrapper e.g. PYMEs' PZFFormat which keeps track of the original data dimensions and dtype (we save a couple of bytes and a seek over using the codec versions above). 

```python

import numpy as np
import pymecompress

data = np.linspace(1,2**15).astype('uint16')

nbytes = data.nbytes
c = pymecompress.HuffmanCompressQuant(data, quantizationOffset, quantizationScale).to_string()
decompressed = pymecompress.HuffmanDecompress(np.fromstring(c, 'u1'), nbytes)
dequantized = (quantisationScale*decompressed)**2 + quantizationOffset

```