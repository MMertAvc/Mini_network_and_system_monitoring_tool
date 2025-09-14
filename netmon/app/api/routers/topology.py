from fastapi import APIRouter, Depends
from sqlalchemy import text
from ...api.deps import get_db

router = APIRouter()

@router.get("")
def get_topology(db=Depends(get_db)):
    devices = [dict(id=r[0], name=r[1], ip=r[2], dtype=r[3]) for r in db.execute(
        text("select id,name,mgmt_ip,dtype from devices where enabled=true"))]
    links = [dict(a=r[0], b=r[1]) for r in db.execute(
        text("select a_dev_id,b_dev_id from links"))]
    return {"nodes": devices, "links": links}