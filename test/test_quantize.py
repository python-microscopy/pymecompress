import numpy as np

def test_loss_within_sigma():
    # fixme preferably this would use bcl.HuffmanCompressQuant directly, not PYME, but documentation is scarce
    from PYME.IO import PZFFormat
    offset = 100
    scale = 1
    ground = np.ascontiguousarray(np.arange(offset, offset + 100, 1).reshape(10, 10).astype('uint16'))

    quantized, header = PZFFormat.loads(PZFFormat.dumps(ground, compression=PZFFormat.DATA_COMP_HUFFCODE,
                                                        quantization=PZFFormat.DATA_QUANT_SQRT,
                                                        quantizationOffset=offset, quantizationScale=scale))

    assert np.all(np.less_equal(np.abs(ground.astype(float) - quantized.squeeze().astype(float)),
                                 np.sqrt(np.sqrt(scale) * (ground.astype(float) - float(offset)))))