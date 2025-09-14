import os, time, hmac, hashlib, base64, json
from fastapi import HTTPException, Header

SECRET = os.getenv("JWT_SECRET","change_me").encode()
ALG = os.getenv("JWT_ALG","HS256")

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def _ub64(s: str) -> bytes:
    s += '='*(-len(s)%4)
    return base64.urlsafe_b64decode(s)

def jwt_encode(payload: dict) -> str:
    header = {"alg": ALG, "typ": "JWT"}
    h64 = _b64(json.dumps(header, separators=(',',':')).encode())
    p64 = _b64(json.dumps(payload, separators=(',',':')).encode())
    sig = hmac.new(SECRET, f"{h64}.{p64}".encode(), hashlib.sha256).digest()
    return f"{h64}.{p64}.{_b64(sig)}"

def jwt_decode(token: str) -> dict:
    try:
        h64,p64,s64 = token.split('.')
        sig = _ub64(s64)
        exp_sig = hmac.new(SECRET, f"{h64}.{p64}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(sig, exp_sig):
            raise ValueError("bad signature")
        payload = json.loads(_ub64(p64))
        if payload.get('exp') and payload['exp'] < int(time.time()):
            raise ValueError("expired")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")

def require_auth(authorization: str|None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing token")
    token = authorization.split(" ",1)[1]
    return jwt_decode(token)