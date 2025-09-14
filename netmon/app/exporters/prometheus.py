from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import text
from ..models.db import SessionLocal

def metrics_app(environ, start_response):
    registry = CollectorRegistry()
    g_up = Gauge("netmon_device_up", "Device up state (ping_up)", ["device_id","name"], registry=registry)
    g_rtt = Gauge("netmon_ping_rtt_ms", "Last ping RTT ms", ["device_id","name"], registry=registry)

    db = SessionLocal()
    rows = db.execute(text(
        """
      with last as (
        select distinct on (device_id, name) device_id, name, value
        from metrics_raw
        where name in ('ping_up','ping_rtt_ms')
        order by device_id, name, ts desc
      )
      select device_id, name, value from last
    """
    ))
    cache = {}
    for device_id, name, value in rows:
        cache.setdefault(device_id, {})[name] = value
    drows = db.execute(text("select id, name from devices"))
    namemap = {r[0]: r[1] for r in drows}
    db.close()

    for did, vals in cache.items():
        dname = namemap.get(did, str(did))
        if "ping_up" in vals:
            g_up.labels(str(did), dname).set(vals["ping_up"])
        if "ping_rtt_ms" in vals:
            g_rtt.labels(str(did), dname).set(vals["ping_rtt_ms"])

    output = generate_latest(registry)
    headers = [(b"Content-Type", CONTENT_TYPE_LATEST)]
    start_response(b"200 OK", headers)
    return [output]