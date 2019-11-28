# PYMECompress

PYMECompress consists of three parts: 

- a fork of the [Basic Compression Library](https://github.com/MariadeAnton/bcl) (note - this is the most current reference I can find, but our original source predates that repository)
with a heavily optimized huffman coder

- a fast, AVX optimized, quantizer to perform "within noise level" quantization of photon-limited images

- a python wrapper of the above. Note that at this point, only huffman coding and quantization are exposed to python

Together they offer a single core throughput of ~500 -600MB/s
