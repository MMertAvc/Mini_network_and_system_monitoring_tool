def mgmt_ip_from_name(name: str) -> str|None:
    if "@" in name:
        maybe = name.split("@")[-1]
        parts = maybe.split("/")
        return parts[0] if "." in parts[0] else None
    return None

def dtype_from_node(node: dict) -> str:
    nt = (node.get("node_type") or "").lower()
    console = (node.get("console_type") or "").lower()
    if "iosv" in nt or "router" in nt: return "router"
    if "iosvl2" in nt or "switch" in nt: return "switch"
    if "qemu" in nt or "vm" in nt: return "server"
    if "firewall" in nt or "pfsense" in node.get("name"," ").lower(): return "firewall"
    if console in ("vnc","telnet"): return "router"
    return "server"