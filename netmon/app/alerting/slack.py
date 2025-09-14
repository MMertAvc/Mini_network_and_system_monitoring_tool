import os, httpx
URL = os.getenv("SLACK_WEBHOOK_URL","")

def send_slack(text: str):
    if not URL: return
    try:
        httpx.post(URL, json={"text": text}, timeout=5)
    except Exception:
        pass