import io
from pathlib import Path

import numpy as np
from PIL import Image


# Image processing API: success path and critical error handling for cutout endpoint.
class TestRemoveBackgroundAPI:
    def test_remove_background_horse_jpg_returns_png_with_transparency(self, api_client, base_url):
        fixture = Path('/app/tests/fixtures/horse.jpg')
        assert fixture.exists(), 'Missing fixture: /app/tests/fixtures/horse.jpg'

        with fixture.open('rb') as f:
            response = api_client.post(
                f'{base_url}/api/images/remove-background',
                files={'image': ('horse.jpg', f, 'image/jpeg')},
                timeout=90,
            )

        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('image/png')
        assert 'no-store' in response.headers.get('cache-control', '').lower()

        out = Image.open(io.BytesIO(response.content)).convert('RGBA')
        assert max(out.size) <= 1600

        alpha = np.array(out.getchannel('A'))
        near_transparent_ratio = float((alpha <= 15).sum()) / alpha.size
        opaque_ratio = float((alpha >= 245).sum()) / alpha.size

        # Wide thresholds to avoid flaky model variance while still proving real cutout happened.
        assert near_transparent_ratio > 0.20
        assert opaque_ratio > 0.20

    def test_remove_background_supports_webp_input(self, api_client, base_url):
        image = Image.new('RGB', (128, 96), 'white')
        buf = io.BytesIO()
        image.save(buf, format='WEBP', quality=90)
        buf.seek(0)

        response = api_client.post(
            f'{base_url}/api/images/remove-background',
            files={'image': ('test.webp', buf, 'image/webp')},
            timeout=90,
        )

        # Model may reject empty/low-detail motif; both prove format accepted and endpoint handled request.
        assert response.status_code in (200, 422)

    def test_remove_background_preserves_preexisting_alpha(self, api_client, base_url):
        rgba = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        for x in range(30, 90):
            for y in range(30, 90):
                rgba.putpixel((x, y), (220, 80, 60, 255))
        input_alpha = np.array(rgba.getchannel('A'))

        buf = io.BytesIO()
        rgba.save(buf, format='PNG')
        buf.seek(0)

        response = api_client.post(
            f'{base_url}/api/images/remove-background',
            files={'image': ('alpha.png', buf, 'image/png')},
            timeout=90,
        )

        assert response.status_code == 200
        out = Image.open(io.BytesIO(response.content)).convert('RGBA')
        out_alpha = np.array(out.getchannel('A'))
        # Pixels fully transparent in original must stay transparent after alpha-mask multiplication.
        assert np.all(out_alpha[input_alpha == 0] == 0)

    def test_remove_background_rejects_empty_file(self, api_client, base_url):
        response = api_client.post(
            f'{base_url}/api/images/remove-background',
            files={'image': ('empty.png', io.BytesIO(b''), 'image/png')},
            timeout=30,
        )

        assert response.status_code == 422
        body = response.json()
        assert isinstance(body.get('detail'), str)

    def test_remove_background_rejects_malformed_image(self, api_client, base_url):
        fixture = Path('/app/tests/fixtures/malformed_fake.png')
        assert fixture.exists(), 'Missing fixture: /app/tests/fixtures/malformed_fake.png'

        with fixture.open('rb') as f:
            response = api_client.post(
                f'{base_url}/api/images/remove-background',
                files={'image': ('malformed_fake.png', f, 'image/png')},
                timeout=30,
            )

        assert response.status_code == 422
        body = response.json()
        assert isinstance(body.get('detail'), str)

    def test_remove_background_rejects_unsupported_content_type(self, api_client, base_url):
        response = api_client.post(
            f'{base_url}/api/images/remove-background',
            files={'image': ('not_image.txt', io.BytesIO(b'hello world'), 'text/plain')},
            timeout=30,
        )

        # Unsupported type can fail by parser (422) or explicit type validation (415).
        assert response.status_code in (415, 422)
        body = response.json()
        assert isinstance(body.get('detail'), str)

    def test_remove_background_rejects_over_10mb(self, api_client, base_url):
        fixture = Path('/app/tests/fixtures/valid_11mb.jpg')
        assert fixture.exists(), 'Missing fixture: /app/tests/fixtures/valid_11mb.jpg'

        with fixture.open('rb') as f:
            response = api_client.post(
                f'{base_url}/api/images/remove-background',
                files={'image': ('valid_11mb.jpg', f, 'image/jpeg')},
                timeout=30,
            )

        assert response.status_code == 413
        body = response.json()
        assert isinstance(body.get('detail'), str)
