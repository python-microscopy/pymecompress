import numpy as np
import six
from cython.view cimport array as cvarray
cimport cython
from libc.stdint cimport uint16_t, uint8_t
from cpython cimport PyObject_CheckBuffer, PyObject_GetBuffer, PyBuffer_Release, Py_buffer, PyObject, PyBUF_SIMPLE, PyBUF_C_CONTIGUOUS, PyBUF_F_CONTIGUOUS, PyBuffer_IsContiguous

cdef extern from "bcl/huffman.h":
    int Huffman_Compress( unsigned char *inp, unsigned char *out, unsigned int insize ) nogil
    int Huffman_Compress_( unsigned char *inp, unsigned char *out, unsigned int insize ) nogil
    void Huffman_Uncompress( unsigned char *inp, unsigned char *out, unsigned int insize, unsigned int outsize ) nogil

cdef extern from "quantize.h":
    void quantize_u16(uint16_t *data, uint8_t * out, int size, float offset, float scale) nogil
    #void quantize_u16_avx( uint16_t * data, uint8_t * out, int size, float offset, float scale) nogil
    
@cython.boundscheck(False)
def HuffmanCompress(data):
    cdef Py_buffer view
    
    #print('HuffmanCompress')
    
    if data.flags['C_CONTIGUOUS']:
        PyObject_GetBuffer(data, &view, PyBUF_C_CONTIGUOUS)
        #print('saving c contiguous')
        #raise RuntimeError('C contig')
    elif data.flags['F_CONTIGUOUS']:
        PyObject_GetBuffer(data, &view, PyBUF_F_CONTIGUOUS)
        #print('saving fortran contiguous')
        #raise RuntimeError('F contig')
    else:
        raise RuntimeError('Input data should be contiguous')
    
    cdef int dsize = view.len
    
    out = np.zeros(int(dsize*1.01 + 320),'uint8')
    cdef unsigned char [:] ov = out
    
    with nogil:
        
        nb = Huffman_Compress(<uint8_t *>view.buf, &ov[0], dsize)
        
    PyBuffer_Release(&view)
    return out[:nb]

@cython.boundscheck(False)
def HuffmanCompressQuant(data, float offset, float scale):
    cdef Py_buffer view
    
    if not data.dtype == 'u2':
        raise RuntimeError('Expected unsigned short input data')
    
    if data.flags['C_CONTIGUOUS']:
        PyObject_GetBuffer(data, &view, PyBUF_C_CONTIGUOUS)
    elif data.flags['F_CONTIGUOUS']:
        PyObject_GetBuffer(data, &view, PyBUF_F_CONTIGUOUS)
    else:
        raise RuntimeError('Input data should be contiguous')
    
    cdef int dsize = data.size
    
    out = np.zeros(int(dsize*1.01 + 320),'uint8')
    quant = np.zeros(dsize, 'uint8')
    cdef unsigned char [:] ov = out
    cdef unsigned char [:] qv = quant
    
    with nogil:
        quantize_u16(<uint16_t *>view.buf, &qv[0], dsize, offset, scale)
        nb = Huffman_Compress(&qv[0], &ov[0], dsize)
        
    PyBuffer_Release(&view)
    return out[:nb]

@cython.boundscheck(False)    
def HuffmanCompressOrig(unsigned char[:] data):
    out = np.zeros(int(data.shape[0]*1.01 + 320),'uint8')
    cdef unsigned char [:] ov = out
    cdef int dsize = data.shape[0]
    with nogil:
        
        nb = Huffman_Compress_(&data[0], &ov[0], dsize)
    return out[:nb]

@cython.boundscheck(False)   
def HuffmanDecompress(unsigned char[:] data, unsigned int outsize):
    out = np.zeros(outsize,'uint8')
    cdef unsigned char [:] ov = out
    cdef int insize = data.shape[0]
    #cdef int outsize = outsize
    with nogil:
        
        Huffman_Uncompress(&data[0], &ov[0], insize, outsize)
    return out
    
    