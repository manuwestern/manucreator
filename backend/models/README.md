# Local foreground model

`u2netp.onnx` is the small U²-Net foreground-segmentation model, executed locally using ONNX Runtime CPU. Model bytes are bundled so processing does not download weights at request time or send customer photos to a third-party service.

- Architecture / authors: Xuebin Qin et al., U²-Net, https://github.com/xuebinqin/U-2-Net (Apache-2.0).
- Model distribution: https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx
- MD5 verified on download: `8e83ca70e441ab06c318d82300c84806`.
- Input preprocessing and mask normalization follow the published rembg U2netpSession (MIT): https://github.com/danielgatis/rembg/blob/main/rembg/sessions/u2netp.py
- Configure `IMAGE_MODEL_PATH` relative to the backend directory. No API credentials required.