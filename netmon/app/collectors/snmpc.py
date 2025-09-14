from datetime import datetime, timezone
from sqlalchemy import text
from ..models.db import SessionLocal
from pysnmp.hlapi import *

CPU_OID = ObjectType(ObjectIdentity('1.3.6.1.4.1.9.2.1.57.0'))
MEM_OID = ObjectType(ObjectIdentity('1.3.6.1.4.1.2021.4.6.0'))

def _get(ip, community, *objs):
    g = getCmd(SnmpEngine(),
               CommunityData(community, mpModel=1),
               UdpTransportTarget((ip, 161), timeout=1, retries=1),
               ContextData(), *objs)
    err, stat, idx, vals = next(g)
    if err or stat:
        return None
    return {str(o[0].prettyPrint()): float(o[1]) for o in vals}

def collect_snmp_simple(device_id: int, ip: str, community: str="public"):
    vals = _get(ip, community, CPU_OID, MEM_OID) or {}
    ts = datetime.now(timezone.utc)
    db = SessionLocal()
    for k,v in vals.items():
        name = "snmp_cpu_pct" if "9.2.1.57" in k else ("snmp_mem_free_kb" if "2021.4.6" in k else "snmp_value")
        db.execute(text(
          """
          insert into metrics_raw(device_id,check_id,ts,name,value,labels)
          values(:d,:c,:ts,:n,:v,'{}')
          """
        ), dict(d=device_id, c=0, ts=ts, n=name, v=v))
    db.commit(); db.close()