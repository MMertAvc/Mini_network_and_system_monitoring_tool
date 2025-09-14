import os, httpx

BASE = os.getenv("GNS3_URL","http://localhost:3080")

async def list_projects():
    async with httpx.AsyncClient(timeout=10) as cx:
        r = await cx.get(f"{BASE}/v2/projects")
        r.raise_for_status(); return r.json()

async def get_project(project_name: str):
    for p in await list_projects():
        if p.get("name")==project_name: return p
    raise RuntimeError(f"Project {project_name} not found")

async def list_nodes(project_id: str):
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.get(f"{BASE}/v2/projects/{project_id}/nodes")
        r.raise_for_status(); return r.json()

async def list_links(project_id: str):
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.get(f"{BASE}/v2/projects/{project_id}/links")
        r.raise_for_status(); return r.json()

async def pcap_control(project_id: str, node_id: str, adapter: int, start=True):
    action = "start" if start else "stop"
    async with httpx.AsyncClient(timeout=10) as cx:
        r = await cx.post(f"{BASE}/v2/projects/{project_id}/nodes/{node_id}/adapters/{adapter}/pcap/{action}")
        r.raise_for_status(); return r.json()