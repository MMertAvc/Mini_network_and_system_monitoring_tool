import os

def get_secret(key: str, default: str|None=None) -> str|None:
    # Basit env backend — Vault/SSM entegrasyonu sprint-4
    return os.getenv(key, default)