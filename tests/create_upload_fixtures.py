from pathlib import Path
from PIL import Image
import numpy as np


OUT_DIR = Path('/app/tests/fixtures')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def noisy_image(width: int, height: int) -> Image.Image:
    rng = np.random.default_rng(2026)
    data = rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)
    return Image.fromarray(data, mode='RGB')


def write_jpeg(path: Path, size: tuple[int, int], quality: int = 95):
    img = noisy_image(*size)
    img.save(path, format='JPEG', quality=quality, optimize=False)


if __name__ == '__main__':
    write_jpeg(OUT_DIR / 'valid_9mb.jpg', (3200, 3200), quality=95)
    write_jpeg(OUT_DIR / 'valid_11mb.jpg', (3800, 3800), quality=96)
    with open(OUT_DIR / 'malformed_fake.png', 'wb') as f:
        f.write(b'not-a-real-image-but-has-png-extension')
    for name in ['valid_9mb.jpg', 'valid_11mb.jpg', 'malformed_fake.png']:
        p = OUT_DIR / name
        print(name, p.stat().st_size)