# Local foreground extraction

- Wrapper: rembg 2.0.85 (MIT), ONNX Runtime CPU 1.30.0 (MIT).
- Explicit model: U²-Net small `u2netp`; never use the rembg default model.
- Source: https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx
- Upstream: https://github.com/xuebinqin/U-2-Net (Apache-2.0, code/models; dataset obligations must be reviewed by operator).
- File: models/u2netp/u2netp.onnx, 4.57 MB.
- SHA256: 309c8469258dda742793dce0ebea8e6dd393174f89934733ecc8b14c76f4ddd8
- Runtime requires the bundled local file. No model download on customer requests, no image transfer to model providers, no generative AI.
- Model credit: Qin et al., U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection (Pattern Recognition 2020).
- Background removal runs explicitly on button press, CPU concurrency one, two ONNX threads, original preserved, per-guest cache and limit.