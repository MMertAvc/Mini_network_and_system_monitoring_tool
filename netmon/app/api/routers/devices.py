from fastapi import APIRouter, Depends
from sqlalchemy import text
from ...models.schemas import DeviceOut
from ...api.deps import get_db

router = APIRouter()

@router.get("/", response_model=list[DeviceOut])
def list_devices(db=Depends(get_db)):
    rows = db.execute(text("select id,name,mgmt_ip,dtype from devices where enabled=true order by id"))
    return [DeviceOut(id=r[0], name=r[1], mgmt_ip=r[2], dtype=r[3]) for r in rows]