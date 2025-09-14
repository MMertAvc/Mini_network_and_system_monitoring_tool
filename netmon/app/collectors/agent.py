import psutil
from datetime import datetime, timezone
from sqlalchemy import text
from ..models.db import SessionLocal

def collect_agent_local(device_id: int):
    ts = datetime.now(timezone.utc)
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    db = SessionLocal()
    for n,v in (("agent_cpu_pct", cpu), ("agent_mem_pct", mem)):
        db.execute(text(
          """
          insert into metrics_raw(device_id,check_id,ts,name,value,labels)
          values(:d,:c,:ts,:n,:v,'{}')
          """
        ), dict(d=device_id, c=0, ts=ts, n=n, v=v))
    db.commit(); db.close()