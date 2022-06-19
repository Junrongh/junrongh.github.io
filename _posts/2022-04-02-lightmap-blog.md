---
title: 'HDR Lightmap Compression'
date: 2022-04-02
permalink: /posts/2022-04-02-lightmap-blog
tags:
  - lightmap
  - compression
  - hdr
---

How to compress a `.exr` hdr lightmap file into `.webp` format for WebGL rendering

HDR Lightmap Compression
======

What is [Lightmap](https://en.wikipedia.org/wiki/Lightmap): A lightmap is a data structure used in lightmapping, a form of surface caching in which the brightness of surfaces in a virtual scene is pre-calculated and stored in texture maps for later use.

Usually, lightmap is stored as `.exr` or `.hdr` file since it will need higher precision, and the maximum value will probably greater than 1, which traditional 8-bit format images such as `.jpg` or `.png` cannot hold. However, the `.exr` or `.hdr` files are very large, which may lead to a network traffic jam in WebGL render applications. Therefore, we need an appropriate way to compress the lightmap file. We found UE4 provides a good way to process this compression

> [Unreal Engine Lightmap Compression](https://github.com/EpicGames/UnrealEngine/blob/release/Engine/Shaders/Private/LightmapCommon.ush)

**However, this compression still has some limitations.**

## How did UE4 encode and decode a lightmap

The whole calculations can be summed up as shown below:

![workflow](/files/images/posts/UE4LightmapFlow.png)

The python implementation:

```python
import numpy as np
import cv2

def encoder(lo, n_mul, n_add):
    lc = lo * n_mul + n_add
    return lc

def decoder(lc, n_mul, n_add):
    lo = (lc - n_add) / n_mul
    return lo

# Read exr, log and normalization
img_hdr = cv2.imread('test.exr', -1)
img = (np.log2(img_hdr + 0.00390625) + 8.0) / 16.0

v_min = np.min(img)
v_max = np.max(img)
n_mul = 1.0 / (v_max - v_min)
n_add = - v_min / (v_max - v_min)

encoded_jpg = encoder(img, n_mul, n_add)

# Saved as jpg, png or webp file for network transmission
cv2.imwrite('test.jpg', np.floor(encoded_jpg * 255.0))

# Use shader to decode this image
encoded_jpg = cv2.imread('test.jpg', -1) / 255.0

res = decoder(encoded_jpg, n_mul, n_add)

res = np.exp2(res * 16.0 - 8.0) - 0.00390625

# We write a exr file to compare the origin lightmap and decoded one
cv2.imwrite('output.exr', res.astype('float32'))
```

This encoder and decoder do works well in most cases, the appearance of the lightmap looks good, and the network transmission looks fine. However, this algorithm has some limitations. As we compare the decoded lightmap with the original one, we found the difference

- We cannot use jpg format to save lightmap since jpg format involves is a lossy compression. See [JPEG compression](https://www.youtube.com/watch?v=0me3guauqOU) for details.

| Origin Lightmap 2.08M | jpg 181K | Webp 372K |
| --- | --- | --- |
| ![origin](/files/images/posts/originLightmap.png) | ![jpg](/files/images/posts/jpgEncoder.png) | ![origin](/files/images/posts/pngEncoder.png) |

- Float texture saved as 8-bit RGB format is a lossy algorithm. Since we involves `np.floor(encoded_jpg * 255.0)` in our implementation, the precision is lost in our transmission format, no matter `jpg` or `png`

| Origin Lightmap | UE4 encoder |
| --- | --- |
| ![origin](/files/images/posts/originLightmapH.png) | ![ue](/files/images/posts/encodeLightmapH.png) |


## How to perform a lossless compression

In general, we need to use more bit than 8-bit RGB format to save a float RGB texture. Therefore, we choose `png` or `webp`, since we can use an additional 8-bit channel to save more information. The most popular encoders are **RGBE** and **LogLUV** compression. We tried both of them and they performed well in both appearance and network transmission

| Origin Lightmap 2.08M | RGBE encoder 608K | LUV encoder 645K |
| --- | --- | --- |
| ![origin](/files/images/posts/originLightmap1.png) | ![origin](/files/images/posts/rgbeLightmap.png) | ![origin](/files/images/posts/logLUVLightmap.png) |

------