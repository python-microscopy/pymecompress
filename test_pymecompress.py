import numpy as np

def test_compression_lossless_uint16():
    from pymecompress import bcl
    test_data = np.random.poisson(100, 10000).reshape(100,100).astype('uint16')

    result = bcl.HuffmanDecompress(bcl.HuffmanCompress(np.frombuffer(test_data.data, dtype='uint16')),
                                   test_data.nbytes).view(test_data.dtype).reshape(test_data.shape)

    assert np.allclose(result, test_data)

def test_compression_lossless_uint8():
    from pymecompress import bcl
    test_data = np.random.poisson(100, 10000).reshape(100,100).astype('uint8')

    result = bcl.HuffmanDecompress(bcl.HuffmanCompress(np.frombuffer(test_data.data, dtype='uint8')),
                                   test_data.nbytes).view(test_data.dtype).reshape(test_data.shape)

    assert np.allclose(result, test_data)