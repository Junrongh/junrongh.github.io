---
title: 'The Seamlessly Representation Translation of Material BRDFs between Different Renderers and Applications'
date: 2018-12-01
permalink: /posts/2018-12-01-material-blog
tags:
  - BRDFs
  - PBR
  - appearance driven
# link: https://www.kujiale.com
---

In order to exchange material seamlessly between renderers and applications, we proposed a appearance-driven method for approximate translation of material BRDFs

V-Ray Material to Unreal Engine 4 PBR Material
======

> This blog will describe a basic workflow for material translation, the interfaces in this page are only for examples.

In order to allow users explore their V-Ray assets, particularly material assets in real-time rendering application, for example, Unreal Engine 4(UE4), we started a project to exchange material seamlessly between different renderers.

## Parameters

Material representation in V-Ray can be expressed as different BRDFs. However, mostly users are recommended to use a template called [BRDFVRayMtl](https://docs.chaos.com/display/VMAX/VRayMtl), as shown below in `.vrscene` file.

```
BRDFVRayMtl vraymtl {
  opacity=1;
  diffuse=AColor(0.0, 0.0, 0.0, 1.0);
  roughness=0;
  roughness_model=0;
  compensate_camera_exposure=0;
  reflect=AColor(1.0, 1.0, 1.0, 1);
  reflect_glossiness=1.0;
  hilight_glossiness=1.0;
  hilight_glossiness_lock=1;
  fresnel=1;
  fresnel_ior=1.6;
  fresnel_ior_lock=0;
  reflect_subdivs=8;
  reflect_trace=1;
  reflect_depth=5;
  reflect_exit_color=Color(0.0, 0.0, 0.0);
  reflect_dim_distance_on=0;
  reflect_dim_distance=100;
  reflect_dim_distance_falloff=0;
  reflect_affect_alpha=0;
  refract=AColor(0, 0, 0, 1);
  refract_ior=1.6;
  refract_glossiness=1;
  refract_subdivs=8;
  refract_trace=1;
  refract_depth=5;
  refract_exit_color_on=0;
  refract_exit_color=Color(0, 0, 0);
  refract_affect_alpha=0;
  refract_affect_shadows=1;
  self_illumination=AColor(0, 0, 0, 1);
}
```

Exclude the refraction and opacity factor, We selected the most important parameters here.

```typescript
interface BRDFVRayMtl {
  diffuse: [number, number, number];
  reflect: [number, number, number];
  reflectGlossiness: number;
  hilightGlossiness: number;
  hilightGlossinessLock: boolean;
  fresnel: boolean;
  fresnelIor: number;
  fresnelIorLock: boolean;
  refractGlossiness: number;
  selfIllumination: [number, number, number];  
}
```

In UE4, they define their materials [here](https://docs.unrealengine.com/4.27/en-US/RenderingAndGraphics/Materials/]). We summed up the most important parameters as shown below.

```typescript
interface UnrealMtl {
  baseColor: [number, number, number];
  metallic: number;
  roughness: number;
  specular: number;
  emissive: [number, number, number];
}
```

## Experiment

In general, what we need to do is to find a translation function from `BRDFVRayMtl` to `UnrealMtl`. Therefore, we need to control the other variables which will affect the final render result, e.g. lighting, geometry, postprocessing, etc.. We built a scene in both V-Ray and UE4:

| V-Ray | UE4 | Diff |
| --- | --- | --- |
| ![vr](/files/images/posts/5b0b9871ed99462084366912_mtl.png) | ![ue](/files/images/posts/5b0b9871ed99462084366912_pbr.png) | ![diff](/files/images/posts/5b0b9871ed99462084366912_diff.png) |

Then we random all parameters in `BRDFVRayMtl` and `UnrealMtl`, created a large data set for the translation solution. We tried rule-based methods and learning-based methods.

## Data & Result

Finally, we had a well translation result in most cases:

| V-Ray | UE4 | V-Ray | UE4 |
| --- | --- | --- | --- |
| ![vr](/files/images/posts/5a1e5411bc974b5bd3a13004.png) | ![ue](/files/images/posts/5a1e5411bc974b5bd3a13004_pbr_r.png) | ![vr](/files/images/posts/5a1e5411bc974b5bd3a13005.png) | ![ue](/files/images/posts/5a1e5411bc974b5bd3a13005_pbr_r.png) |
| ![vr](/files/images/posts/5a1e5412bc974b5bd3a13006.png) | ![ue](/files/images/posts/5a1e5412bc974b5bd3a13006_pbr_r.png) | ![vr](/files/images/posts/5a728caf4242a67d6cbf5aa0.png) | ![ue](/files/images/posts/5a728caf4242a67d6cbf5aa0_pbr_r.png) |
| ![vr](/files/images/posts/5a925eebb5327622b07f6a89.png) | ![ue](/files/images/posts/5a925eebb5327622b07f6a89_pbr_r.png) | ![vr](/files/images/posts/5a9747e652b61463f5392411.png) | ![ue](/files/images/posts/5a9747e652b61463f5392411_pbr_r.png) |

Compare with [V-Ray for Unreal plugin](https://www.chaos.com/vray/unreal), our translation performs better, especially in metallic and roughness term:

| V-Ray | Ours | V-Ray for Unreal Plugin |
| --- | --- | --- |
| ![vr](/files/images/posts/62a8094b6d8f3a000178cadf_vray.jpg) | ![ours](/files/images/posts/62a8094b6d8f3a000178cadf_ours.png) | ![plugin](/files/images/posts/62a8094b6d8f3a000178cadf_plugin.png) |
| ![vr](/files/images/posts/62a8094b6d8f3a000178cae9_vray.jpg) | ![ours](/files/images/posts/62a8094b6d8f3a000178cae9_ours.png) | ![plugin](/files/images/posts/62a8094b6d8f3a000178cae9_plugin.png) |
| ![vr](/files/images/posts/62a8094c6d8f3a000178caf2_vray.jpg) | ![ours](/files/images/posts/62a8094c6d8f3a000178caf2_ours.png) | ![plugin](/files/images/posts/62a8094c6d8f3a000178caf2_plugin.png) |


## Limitations

However, this translation cannot perform well in all cases, for example:

| V-Ray | UE4 | V-Ray | UE4 |
| --- | --- | --- | --- |
| ![vr](/files/images/posts/5a8e99814242a67d6cbfa740_mtl.png) | ![ue](/files/images/posts/5a8e99814242a67d6cbfa740_pbr.png) | ![vr](/files/images/posts/5b0ba8eea25e6b110ffd68fb_mtl.png) | ![ue](/files/images/posts/5b0ba8eea25e6b110ffd68fb_pbr.png) |
| ![vr](/files/images/posts/5b026c85a25e6b3bba7dab5f_mtl.png) | ![ue](/files/images/posts/5b026c85a25e6b3bba7dab5f_pbr.png) | ![vr](/files/images/posts/5b0be75eb5327641b689a856_mtl.png) | ![ue](/files/images/posts/5b0be75eb5327641b689a856_pbr.png) |

It can be explained by the theory of degree of freedom. In `BRDFVRayMtl`, it has `diffuse`, `reflect` that are in `RGB` space, while in `UnrealMtl` only `baseColor` can be expressed in `RGB` space. Therefore, we can only seamlessly translate the representation of materials between this two applications since we lost some degree of freedom in this translation.

## Discussion

Different render applications have their own implementations of material BRDFs, while some of them are not open sourced, e.g. Chaos V-Ray. Chaos did implemented a [V-Ray for Unreal plugin](https://www.chaos.com/vray/unreal) to allow their users to export their V-Ray assets to UE4, but as they described, 

> Automatically converts V-Ray materials to approximate Unreal materials. Original V-Ray materials are used when rendering.

the appearance of material in UE4 real-time rendering is not guaranteed.

In this blog, we generally proposed a workflow that allow material representation translation between different render applications. 

------