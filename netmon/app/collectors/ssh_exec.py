import paramiko

def run_ssh(ip: str, username: str, password: str, cmd: str) -> str:
    c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username=username, password=password, timeout=5)
    _, stdout, _ = c.exec_command(cmd, timeout=5)
    out = stdout.read().decode("utf-8","ignore")
    c.close()
    return out