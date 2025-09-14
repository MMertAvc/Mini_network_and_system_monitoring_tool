from pythonping import ping
from datetime import datetime, timezone
from sqlalchemy import text
from ..models.db import SessionLocal

def collect_ping(device_id: int, ip: str, count=3, timeout=1.0):
    r = ping(ip, count=count, timeout=timeout, size=32)
    success = sum(1 for resp in r if resp.success)
    loss = 100.0 - (success / count * 100.0)
    rtts = [resp.time_elapsed_ms for resp in r if resp.success]
    rtt_avg = sum(rtts)/len(rtts) if rtts else 0.0
    up = 1.0 if loss < 100.0 else 0.0
    ts = datetime.now(timezone.utc)
    db = SessionLocal()
    for name, val in (("ping_loss_pct", loss), ("ping_rtt_ms", rtt_avg), ("ping_up", up)):
        db.execute(text(
          """
          insert into metrics_raw(device_id,check_id,ts,name,value,labels)
          values(:d,:c,:ts,:n,:v,'{}')
          """
        ), dict(d=device_id, c=0, ts=ts, n=name, v=val))
    db.commit(); db.close()