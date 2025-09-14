import httpx
from datetime import datetime, timezone
from sqlalchemy import text
from ..models.db import SessionLocal

async def collect_http(device_id: int, url: str, expect_status=200):
    ts = datetime.now(timezone.utc)
    up, lat = 0.0, 0.0
    async with httpx.AsyncClient(timeout=5.0, verify=True) as cx:
        try:
            resp = await cx.get(url)
            up = 1.0 if resp.status_code == expect_status else 0.0
            lat = resp.elapsed.total_seconds()*1000.0
        except Exception:
            up = 0.0; lat = 0.0
    db = SessionLocal()
    for n,v in (("http_up", up), ("http_latency_ms", lat)):
        db.execute(text(
          """
          insert into metrics_raw(device_id,check_id,ts,name,value,labels)
          values(:d,:c,:ts,:n,:v,'{}')
          """
        ), dict(d=device_id, c=0, ts=ts, n=n, v=v))
    db.commit(); db.close()