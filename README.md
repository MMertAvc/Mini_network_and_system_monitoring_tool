### Mini_network_and_system_monitoring_tool
## Hızlı doğrulama 
# sanal ortam
python -m venv .venv
.\.venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp .env.example .env
# .env içini doldur (GNS3_URL, GNS3_PROJECT, DB_URL)

alembic upgrade head
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# GNS3 envanter senkronu
python -c "from app.inventory.sync import run; run()"

# Ping check ekleme
python - <<'PY'
from app.models.db import SessionLocal
from app.models.core import Device, Check
db=SessionLocal()
for d in db.query(Device).filter(Device.mgmt_ip!=None, Device.enabled==True):
    db.add(Check(device_id=d.id, ctype="ping", params={}, interval_s=10, enabled=True))
db.commit(); db.close()
print("Ping checks eklendi.")
PY

# Scheduler
python -m app.workers.scheduler


Kontrol:

http://localhost:8000/health

http://localhost:8000/devices

http://localhost:8000/topology

http://localhost:8000/ui/topology/index.html

http://localhost:8000/metrics
