# PYMECompress

PYMECompress consists of three parts: 

- a fork of the Basic Compression Library originally by Marcus Geelnard, 
modified to include a heavily optimized huffman coder (BCL license is avalable under pymecompress/doc/manual.pdf and would appear to be BSD compatible)

- a fast, AVX optimized, quantizer to perform "within noise level" quantization of photon-limited images

- a python wrapper of the above. Note that at this point, only huffman coding and quantization are exposed to python

Together they offer a single core throughput of ~500 -600MB/s
