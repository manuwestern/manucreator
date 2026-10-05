"""One explicit origin policy for credentialed CORS and admin CSRF checks."""
import os
from urllib.parse import urlsplit


def explicit_origins():
    origins=[]
    for entry in os.environ['CORS_ORIGINS'].split(','):
        value=entry.strip()
        if not value or value=='*':
            # A wildcard must NEVER authorize credentialed administration.
            continue
        try:
            parsed=urlsplit(value)
            if (parsed.scheme not in {'http','https'} or not parsed.hostname
                    or parsed.username is not None or parsed.password is not None
                    or parsed.path not in {'','/'} or parsed.query or parsed.fragment
                    or '*' in parsed.netloc):
                continue
            host=parsed.hostname.encode('idna').decode('ascii').lower()
            if any(char.isspace() for char in host) or '\\' in host:
                continue
            if ':' in host:
                host=f'[{host}]'
            port=parsed.port
            default_port=443 if parsed.scheme=='https' else 80
            authority=host if port is None or port==default_port else f'{host}:{port}'
            origin=f'{parsed.scheme}://{authority}'
        except (ValueError,UnicodeError):
            continue
        if origin not in origins:
            origins.append(origin)
    return origins