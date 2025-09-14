from fastapi import APIRouter, Depends
from sqlalchemy import text
from ...models.schemas import CheckOut
from ...api.deps import get_db

router = APIRouter()

@router.get("/", response_model=list[CheckOut])
def list_checks(db=Depends(get_db)):
    rows = db.execute(text("select id, device_id, ctype, params, interval_s, enabled from checks order by id"))
    return [CheckOut(id=r[0], device_id=r[1], ctype=r[2], params=r[3], interval_s=r[4], enabled=r[5]) for r in rows]