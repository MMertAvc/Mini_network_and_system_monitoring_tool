from fastapi import APIRouter
router = APIRouter()
# Basit iskelet — genişletilebilir
@router.get("/")
def list_alerts():
    return []