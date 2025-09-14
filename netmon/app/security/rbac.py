from fastapi import HTTPException

def check_role(user: dict, role: str):
    roles = user.get('roles', [])
    if role not in roles:
        raise HTTPException(status_code=403, detail="forbidden")