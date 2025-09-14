import os, asyncio
from sqlalchemy import text
from ..models.db import SessionLocal
from ..inventory.gns3_api import get_project, pcap_control

def start_pcap_for_device(device_id: int, adapter: int=0):
    db = SessionLocal()
    row = db.execute(text("select gns3_id from devices where id=:i"), {"i": device_id}).first()
    db.close()
    if not row: return
    gid = row[0]
    async def _run():
        pj = await get_project(os.getenv("GNS3_PROJECT","CampusLab"))
        await pcap_control(pj["project_id"], gid, adapter, start=True)
    asyncio.run(_run())