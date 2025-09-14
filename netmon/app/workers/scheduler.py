import time
from sqlalchemy import text
from ..models.db import SessionLocal
from .tasks import task_ping, task_http, task_snmp

def run_light_scheduler(project_name: str="CampusLab"):
    last = {}
    while True:
        db = SessionLocal()
        rows = db.execute(text(
          """
          select c.id, d.id as device_id, d.mgmt_ip, c.ctype, c.params, c.interval_s
          from checks c join devices d on d.id=c.device_id
          where c.enabled=true and d.enabled=true
          """
        ))
        now = time.time()
        for cid, did, ip, ctype, params, interval_s in rows:
            key = (cid,)
            if now - last.get(key, 0) >= interval_s:
                if ctype=="ping" and ip:
                    task_ping.delay(did, ip)
                elif ctype=="http":
                    url = (params or {}).get("url")
                    expect = (params or {}).get("expect", 200)
                    if url: task_http.delay(did, url, expect)
                elif ctype=="snmp" and ip:
                    comm = (params or {}).get("community","public")
                    task_snmp.delay(did, ip, comm)
                last[key]=now
        db.close()
        time.sleep(1)

if __name__ == "__main__":
    run_light_scheduler()