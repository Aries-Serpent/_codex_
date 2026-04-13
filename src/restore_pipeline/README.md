# restore_pipeline

CPU-only image restoration + vivid colorization pipeline for Python 3.12.

> **No GPU required. No model training performed.**

---

## Features

| Stage | Method | Status |
|-------|--------|--------|
| Noise estimation | `skimage.restoration.estimate_sigma` | ✅ default |
| Denoising | BM3D → cv2 NL-means → skimage NL-means (fallback chain) | ✅ default |
| Deblurring | Richardson–Lucy (`skimage.restoration.richardson_lucy`) | opt-in `--deblur` |
| Inpainting | `cv2.inpaint` INPAINT_TELEA | opt-in `--mask` |
| Color enhancement | CLAHE on L + saturation boost (LAB space); optional Reinhard transfer when `--reference` given | ✅ default |
| Colorization | ONNX CPUExecutionProvider | opt-in `--colorize` |
| Sharpening | Unsharp mask | ✅ default |
| Metrics | PSNR + SSIM (`skimage.metrics`) | when `--reference` given |

---

## Installation

```bash
pip install -r src/restore_pipeline/requirements.txt
export PYTHONPATH="$PWD/src"
```

Or with the Makefile:

```bash
make install
```

---

## Quick start

```bash
# Restore a single image
python -m restore_pipeline.cli --input photo.jpg --output ./restored --verbose

# Batch (folder)
python -m restore_pipeline.cli --input ./raw_photos --output ./restored

# With inpainting mask
python -m restore_pipeline.cli --input photo.jpg --mask mask.png --output ./out

# With deblurring enabled
python -m restore_pipeline.cli --input blurry.jpg --deblur --output ./out

# Full demo (creates synthetic noisy image → restores → prints metrics)
bash examples/run_demo.sh
```

---

## CLI options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | *(required)* | Image file or folder |
| `--output` | *(required)* | Output directory |
| `--mask` | None | Binary mask for inpainting (non-zero = repair) |
| `--reference` | None | Ground-truth image for metrics + Reinhard color transfer |
| `--algorithm` | `auto` | `auto` \| `bm3d` \| `nl_means` \| `opencv` |
| `--deblur` | off | Enable Richardson–Lucy deblurring |
| `--psf` | None | PSF image path (Gaussian kernel used when absent) |
| `--colorize` | off | Enable ONNX colorization (see below) |
| `--colorize-model` | None | Path to colorization ONNX model |
| `--verbose` | off | Debug logging |

---

## Python API

```python
from restore_pipeline import process, PipelineConfig
import numpy as np

# Load image as float32 [0,1] or uint8
image: np.ndarray = ...

# Basic restoration
restored_u8, metrics = process(image)

# Full control
cfg = PipelineConfig(
    algorithm="bm3d",
    deblur=True,
    saturation_scale=1.5,
)
restored_u8, metrics = process(
    image,
    mask=mask_array,      # optional
    reference=ref_array,  # optional — enables metrics
    config=cfg,
)

print(metrics)
# {'elapsed_seconds': 0.42, 'psnr_restored': 34.1, 'ssim_restored': 0.91,
#  'psnr_degraded': 28.3, 'ssim_degraded': 0.76, ...}
```

---

## Metrics

| Metric | Function | Notes |
|--------|----------|-------|
| PSNR | `skimage.metrics.peak_signal_noise_ratio` | dB; higher = better |
| SSIM | `skimage.metrics.structural_similarity` | [−1,1]; higher = better |

Metrics are only computed when a `--reference` image is provided (or `reference=` in the API).

---

## Opt-in: ONNX Colorization

Colorization is disabled by default. To enable it:

1. **Download a colorization ONNX model.** One compatible open-source model is the
   Zhang et al. (2016) model converted to ONNX:

   | Item | Detail |
   |------|--------|
   | Original paper | [Colorful Image Colorization](https://richzhang.github.io/colorization/) |
   | License | [BSD 2-Clause](https://github.com/richzhang/colorization/blob/caffe/LICENSE) |
   | Reference URL | `https://github.com/richzhang/colorization` |
   | Model file | Not bundled — must be downloaded separately (see below) |

   > **The model file is NOT committed to this repository** (binary > 5 MB).

2. **Download the model:**

   ```bash
   # Community ONNX export — verify checksum before use
   wget -O models/colorize.onnx <YOUR_ONNX_MODEL_URL>
   ```

3. **Run with colorization:**

   ```bash
   python -m restore_pipeline.cli \
       --input grayscale.jpg \
       --output ./colored \
       --colorize \
       --colorize-model ./models/colorize.onnx
   ```

> `onnxruntime` is always invoked with `providers=["CPUExecutionProvider"]`.
> GPU providers are never auto-selected.

---

## Design decisions

- **BM3D first, graceful fallback**: BM3D produces state-of-the-art denoising quality on CPU.
  If `bm3d` is not installed (rare), the pipeline silently falls back to scikit-image NL-means.
- **LAB colour space for CLAHE**: CLAHE applied only to the luminance channel (L) avoids
  colour artefacts that occur when histogram equalisation is applied to RGB directly.
- **No model files > 5 MB**: All pre-trained models are downloaded on demand via documented URLs.
- **Python 3.12 native types**: Uses `X | Y`, `list[...]`, `dict[...]`, `tomllib`, and
  `datetime.now(timezone.utc)` throughout — no deprecated `typing.*` aliases.

---

## Running tests

```bash
pytest src/restore_pipeline/tests/ -q --tb=short -W error
```

All tests are self-contained (synthetic images generated at runtime — no external files needed).

---

## Docker

```bash
docker build -f Dockerfile.restore -t restore-pipeline .
docker run --rm restore-pipeline --help

# Process a local image
docker run --rm \
    -v /path/to/images:/data \
    restore-pipeline --input /data/photo.jpg --output /data/restored
```

---

## Makefile targets

```bash
make install      # pip install requirements
make run-sample   # run examples/run_demo.sh
make test         # pytest
```
