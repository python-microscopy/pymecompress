//
//  quantize.c
//
//  Created by David Baddeley on 6/11/16.
//  Copyright © 2016 David Baddeley. All rights reserved.
//

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
//#include <x86intrin.h>

#include "quantize.h"

#ifdef __AVX__
#pragma message "AVX defined"
#include <immintrin.h>
#endif

#ifdef __AVX2__
#pragma message "AVX2 defined"
#endif

//#include "systimer.h"

// #define TESTSIZE (2000*2000)
// #define NUMITERS 10
// #define NUMITERS_1 1000

// //#ifndef __AVX__
// /* use slower code*/
// /* square root quantize data, with a given offset and scale*/
// void quantize_u16_noavx(uint16_t *data, uint8_t * out, int size, float offset, float scale)
// {
//     float qs = 1.0/scale;
//     int i = 0;

//     for (i = 0; i < size; i++)
//     {
//         out[i] = (uint8_t) roundf(qs*sqrtf(data[i] - offset));
//     }
// }

// //#else

// //#ifdef __AVX__
// /* square root quantize data, with a given offset and scale
// uses avx command set to process 16 values in parallel
// */
// void quantize_u16_avx(uint16_t * data, uint8_t * out, int size, float offset, float scale)
// {
//     float qs = 1.0/scale;
//     int i = 0;

//     __m256 x, x1, xs;
//     __m128i t2, xlo, xhi, xp1, xp2, xpp;
//     __m256i combined, xi, xp;

//     __m256 offs;
//     __m256 sc;
//     offs = _mm256_set1_ps(offset);
//     sc = _mm256_set1_ps(qs);

//     /* process 16 values at a time - only do the aligned bit */
//     for (i = 0; i < (16*(size/16)); i+=16)
//     {
//         /* process first 8 values */
//         t2 = _mm_load_si128((__m128i *) &(data[i]));
//         xlo = _mm_unpacklo_epi16(t2, _mm_set1_epi16(0));
//         xhi = _mm_unpackhi_epi16(t2, _mm_set1_epi16(0));
//         //xhi = _mm_unpackhi_epi16( _mm_set1_epi16(0), t2);
//         //combined = (__m256i)_mm256_loadu2_m128i (&xhi, &xlo);
//         combined = _mm256_insertf128_si256(_mm256_castsi128_si256(_mm_loadu_si128(&xlo)),_mm_loadu_si128(&xhi),1);
//         x = (__m256)_mm256_cvtepi32_ps(combined);
//         x1 = (__m256)_mm256_sub_ps(x, offs);
//         xs = (__m256)_mm256_mul_ps(_mm256_mul_ps(_mm256_rsqrt_ps(x1),x1), sc);
//         //xs = _mm256_mul_ps(_mm256_sqrt_ps(x1), sc);
//         xi = (__m256i)_mm256_cvtps_epi32 (xs);
//         xp = xi;
//         //xp = _mm256_packs_epi32 (xi, _mm256_set1_epi32 (0));
//         //xp = _mm256_packs_epi16 (xp, _mm256_set1_epi16 (0));
//         /*xp =  _mm256_shuffle_epi8 (xi, _mm256_set_epi8(0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80,
//                                                        0x80, 0x80, 0x80, 0x80, 28, 24, 20, 16,
//                                                        0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80,
//                                                        0x80, 0x80, 0x80, 0x80, 12,   8,  4,  0));
//         */
//          xp1 = _mm_packus_epi16 (_mm256_extractf128_si256 (xp, 0), _mm256_extractf128_si256 (xp, 1));

//         /* process next 8 values */
//         t2 = _mm_load_si128((__m128i *) (&(data[i+8])));
//         xlo = _mm_unpacklo_epi16(t2, _mm_set1_epi16(0));
//         xhi = _mm_unpackhi_epi16(t2, _mm_set1_epi16(0));
//         //combined = (__m256i)_mm256_loadu2_m128i (&xhi, &xlo);
//         combined = _mm256_insertf128_si256(_mm256_castsi128_si256(_mm_loadu_si128(&xlo)),_mm_loadu_si128(&xhi),1);
//         x = (__m256)_mm256_cvtepi32_ps(combined);
//         x1 = (__m256)_mm256_sub_ps(x, offs);
//         xs = (__m256)_mm256_mul_ps(_mm256_mul_ps(_mm256_rsqrt_ps(x1),x1), sc);
//         //xs = _mm256_mul_ps(_mm256_sqrt_ps(x1), sc);
//         xi = (__m256i)_mm256_cvtps_epi32 (xs);
//         xp = xi;
//         //xp = _mm256_packs_epi32 (xi, _mm256_set1_epi32 (0));
//         //xp2 = _mm256_extractf128_si256 (xp, 0);
//         xp2 = _mm_packus_epi16 (_mm256_extractf128_si256 (xp, 0), _mm256_extractf128_si256 (xp, 1));

//         xpp = _mm_packus_epi16 (xp1, xp2);
//         _mm_store_si128((__m128i *)&(out[i]), xpp);

//         //out += 16

//         //out[i] = qs*sqrtf(data[i] - offset);
//     }

//     //do the unaligned bit
//     for (; i < size; i++)
//     {
//         out[i] = (uint8_t) roundf(qs*sqrtf(data[i] - offset));
//     }
// }

//#endif

#define GCC_VERSION (__GNUC__ * 10000 + __GNUC_MINOR__ * 100 + __GNUC_PATCHLEVEL__)
#define _STR(x) #x
#define STR(x) _STR(x)

#pragma message ("GCC_VERSION=" STR(GCC_VERSION)) 

/* Test for GCC > 3.2.0  - note that __builtin_cpu_supports is broken on OSX, hence we have to exclude clang*/
#if (GCC_VERSION > 40200) && !defined(__aarch64__) //&& !defined(__clang__)

void quantize_u16(uint16_t *data, uint8_t * out, int size, float offset, float scale)
{
    if (__builtin_cpu_supports("avx"))
    {
        printf("Using AVX optimsed code\n");
        _quantize_u16_AVX(data, out, size, offset, scale);
    }else
    {
        _quantize_u16(data, out, size, offset, scale);
    }
}

#else
    #ifndef __aarch64__
    #warning Using an old version of GCC - runtime avx detection disabled and compiling for native architecture. Please use GCC > 4.8
    #endif

    #ifndef __AVX__
        void quantize_u16(uint16_t *data, uint8_t * out, int size, float offset, float scale)
        {
            _quantize_u16(data, out, size, offset, scale);
        }
     #else
        void quantize_u16(uint16_t *data, uint8_t * out, int size, float offset, float scale)
        {
            _quantize_u16_AVX(data, out, size, offset, scale);
        }
     #endif


#endif