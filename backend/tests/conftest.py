import os
from pathlib import Path

import pytest
import requests


def _load_base_url_from_frontend_env() -> str:
    env_file = Path('/app/frontend/.env')
    if not env_file.exists():
        return ''
    for line in env_file.read_text(encoding='utf-8').splitlines():
        if line.startswith('REACT_APP_BACKEND_URL='):
            return line.split('=', 1)[1].strip()
    return ''


@pytest.fixture(scope='session')
def base_url() -> str:
    """Public API base URL (external preview) used for all backend regression tests."""
    url = os.environ.get('REACT_APP_BACKEND_URL') or _load_base_url_from_frontend_env()
    if not url:
        pytest.skip('REACT_APP_BACKEND_URL is missing; backend API tests skipped.')
    return url.rstrip('/')


@pytest.fixture(scope='session')
def api_client() -> requests.Session:
    """Shared HTTP session for API endpoint checks."""
    session = requests.Session()
    session.headers.update({'Accept': 'application/json'})
    return session
