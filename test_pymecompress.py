import numpy as np

def test_compression_lossless_uint16():
    from pymecompress import bcl
    test_data = np.random.poisson(100, 10000).reshape(100,100).astype('uint16')

    result = bcl.HuffmanDecompress(bcl.HuffmanCompress(np.frombuffer(test_data.data, dtype='uint8')),
                                   test_data.nbytes).view(test_data.dtype).reshape(test_data.shape)

    assert np.allclose(result, test_data)

def test_compression_lossless_uint8():
    from pymecompress import bcl
    test_data = np.random.poisson(100, 10000).reshape(100,100).astype('uint8')

    result = bcl.HuffmanDecompress(bcl.HuffmanCompress(np.frombuffer(test_data.data, dtype='uint8')),
                                   test_data.nbytes).view(test_data.dtype).reshape(test_data.shape)

    assert np.allclose(result, test_data)

def test_loss_within_sigma():
    from pymecompress import bcl
    offset = 100
    scale = 1
    ground = np.ascontiguousarray(np.arange(offset, offset + 100, 1).reshape(10, 10).astype('uint16'))

    quantized = bcl.HuffmanDecompress(bcl.HuffmanCompressQuant(np.frombuffer(ground.data, dtype='uint16'), offset,
                                                               scale),
                                      int(ground.nbytes / 2)).reshape(ground.shape)
    quantized = (quantized.astype(float) * scale) ** 2 + offset

    assert np.all(
        np.less_equal(np.abs(ground.astype(float) - quantized.squeeze().astype(float)),
                      np.sqrt(np.sqrt(scale) * (ground.astype(float) - float(offset))))
    )
