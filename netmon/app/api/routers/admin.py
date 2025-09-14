from fastapi import APIRouter
router = APIRouter()
@router.get("/info")
def info():
    return {"app":"netmon","version":"0.1.0"}