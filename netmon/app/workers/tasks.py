from .celery_app import app
from ..collectors.icmp import collect_ping
from ..collectors.httpc import collect_http
from ..collectors.snmpc import collect_snmp_simple

@app.task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries":3})
def task_ping(device_id: int, ip: str):
    collect_ping(device_id, ip)

@app.task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries":3})
def task_http(device_id: int, url: str, expect: int=200):
    import anyio; anyio.run(collect_http, device_id, url, expect)

@app.task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries":3})
def task_snmp(device_id: int, ip: str, community="public"):
    collect_snmp_simple(device_id, ip, community)