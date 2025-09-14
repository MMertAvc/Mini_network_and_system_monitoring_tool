import os, asyncio
from sqlalchemy import text
from ..models.db import SessionLocal
from .gns3_api import get_project, list_nodes, list_links
from .classify import mgmt_ip_from_name, dtype_from_node

async def sync_inventory(project_name: str):
    db = SessionLocal()
    pj = await get_project(project_name)
    pid = pj["project_id"]
    nodes = await list_nodes(pid)
    links = await list_links(pid)

    for n in nodes:
        name = n["name"]
        gns3_id = n["node_id"]
        mgmt_ip = mgmt_ip_from_name(name) or n.get("properties",{}).get("ip")
        dtype = dtype_from_node(n)
        db.execute(text(
            """
            insert into devices (gns3_id,name,mgmt_ip,dtype,labels,enabled)
            values (:gid,:name,:ip,:dtype,'{}',true)
            on conflict (name) do update set mgmt_ip = excluded.mgmt_ip, dtype=excluded.dtype
            """
        ), dict(gid=gns3_id, name=name, ip=mgmt_ip, dtype=dtype))
    db.commit()

    idmap = {r[1]: r[0] for r in db.execute(text("select id,gns3_id from devices"))}

    for l in links:
        nodes_ = l.get("nodes", [])
        if len(nodes_)!=2: continue
        a, b = nodes_[0], nodes_[1]
        a_id = idmap.get(a["node_id"]); b_id = idmap.get(b["node_id"])
        if not a_id or not b_id: continue
        db.execute(text(
            """
            insert into links (gns3_id, a_dev_id, b_dev_id, a_if, b_if, meta)
            values (:gid,:a,:b,:aif,:bif,'{}')
            on conflict do nothing
            """
        ), dict(gid=l["link_id"], a=a_id, b=b_id,
                   aif=str(a.get("adapter_number")), bif=str(b.get("adapter_number"))))
    db.commit(); db.close()

def run(project_name: str|None=None):
    name = project_name or os.getenv("GNS3_PROJECT","CampusLab")
    asyncio.run(sync_inventory(name))