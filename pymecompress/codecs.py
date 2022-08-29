"""
numcodecs compatible compression and quantization codecs.
"""
from . import bcl
import numcodecs
from numcodecs.abc import Codec


class Huffman(Codec):
    codec_id='pymecompress-huffman'
    
    def encode(self, buf):
        return bcl.huffman_compress_buffer(buf)
    
    def decode(self, buf, out=None):
        return bcl.huffman_decompress_buffer(buf, out)
        
    def get_config(self):
        return {'codec_id': self.codec_id}
    
    @classmethod
    def from_config(cls, config):
        return cls()

numcodecs.register_codec(Huffman)

class HuffmanQuant16(Codec):
    codec_id = 'pymecompress-quant16'
    
    def __init__(self, offset=0, scale=1):
        self._offset = offset
        self._scale = scale
    
    def encode(self, buf):
        return bcl.huffman_compress_quant_buffer(buf, self._offset, self._scale)
    
    def decode(self, buf, out=None):
        ret = bcl.huffman_decompress_buffer(buf, None).astype('uint16')
        
        ret = (ret*ret)/self._scale + self._offset
        
        if out is None:
            out = ret
        else:
           out[:] = ret
        
        return out.astype('uint16')
    
    def get_config(self):
        return {'codec_id': self.codec_id,
                'offset': self._offset, 'scale' : self._scale}
    
    @classmethod
    def from_config(cls, config):
        return cls(offset=config.get('offset', 0), scale=config.get('scale', 1))

numcodecs.register_codec(HuffmanQuant16)
