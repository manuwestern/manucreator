"""Iteration 25: image_shape acceptance/rejection on POST /api/studio/drafts."""
import os, uuid, requests, pytest

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000').rstrip('/')


@pytest.fixture(scope='module')
def guest():
    s = requests.Session()
    r = s.post(f'{BASE_URL}/api/studio/session', json={}, timeout=20)
    assert r.status_code == 200, r.text
    tok = r.json().get('access_token') or r.json().get('token')
    assert tok
    s.headers.update({'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'})
    return s


@pytest.fixture(scope='module')
def product_id(guest):
    r = guest.get(f'{BASE_URL}/api/studio/products', timeout=20)
    assert r.status_code == 200
    data = r.json()
    items = data.get('products') if isinstance(data, dict) else data
    assert items, 'need at least one product seeded'
    return items[0].get('id') or items[0].get('product_id') or items[0].get('_id') or items[0].get('name')


def _draft_payload(pid, shape='rect'):
    return {
        'product_id': pid,
        'template': 'text',
        'editor_mode': 'free',
        'elements': [{
            'id': f'el{uuid.uuid4().hex[:8]}',
            'kind': 'text',
            'x': 0.1, 'y': 0.1, 'w': 0.3, 'h': 0.1,
            'text': 'TEST_shape',
            'font': 'sans',
            'font_size': 32,
            'image_shape': shape,
        }],
    }


@pytest.mark.parametrize('shape', ['rect', 'circle', 'ellipse', 'heart'])
def test_image_shape_accepted(guest, product_id, shape):
    r = guest.post(f'{BASE_URL}/api/studio/drafts', json=_draft_payload(product_id, shape), timeout=30)
    assert r.status_code in (200, 201), f'{shape}: {r.status_code} {r.text[:300]}'
    data = r.json()
    els = (data.get('design') or data.get('config') or {}).get('elements') or data.get('elements') or []
    assert els, f'no elements persisted in {data}'
    assert els[0]['image_shape'] == shape


@pytest.mark.parametrize('shape', ['triangle', 'oval', '', 'square', 'RECT'])
def test_image_shape_rejected(guest, product_id, shape):
    r = guest.post(f'{BASE_URL}/api/studio/drafts', json=_draft_payload(product_id, shape), timeout=30)
    assert r.status_code in (400, 422), f'{shape}: {r.status_code}'
