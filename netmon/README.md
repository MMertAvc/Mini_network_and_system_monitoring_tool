# NetMon (GNS3 tabanlı Zabbix-benzeri İzleme)

## Kurulum
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`
3) `cp .env.example .env` ve düzenle
4) `docker compose up -d`
5) `alembic upgrade head`
6) API: `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`
7) Worker: `celery -A app.workers.celery_app.app worker -l info --concurrency 4`
8) Scheduler: `python -m app.workers.scheduler`
9) Envanter senk: `python -c "from app.inventory.sync import run; run()"`

## Testler
`pytest -q`

### Detaylı Anlatım (Farklı Cihazdaki GNS3 için)
NetMon – GNS3 tabanlı Zabbix-benzeri İzleme (Docker’sız Kurulum Rehberi)

Bu proje; GNS3 topolojinizi programatik keşfeder, envanteri veritabanına yazar, cihazlardan PING/HTTP/SNMP/Agent metrikleri toplar, veriyi saklar ve /metrics üzerinden Prometheus formatında sunar. Basit bir topoloji haritası (D3.js) ve temel kural/alert akışı da içerir.

Bu README, Docker kullanmadan, uzaktaki GNS3 ile nasıl bağlanıp test edeceğinizi adım adım anlatır. İsterseniz yerel (dummy) test de yapabilirsiniz.

0) Hızlı Özet (TL;DR)
# 1) Python ortamı
python -m venv .venv && source .venv/bin/activate   # Win: .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 2) .env düzenle (uzaktaki GNS3 IP ve proje adını yaz)
# örn:
# GNS3_URL=http://10.0.0.50:3080
# GNS3_PROJECT=CampusLab
# DB_URL=postgresql+psycopg2://netmon:netmon@localhost:5432/netmon   (Postgres önerilir)

# 3) Veritabanı şeması
alembic upgrade head    # (Timescale yoksa hata alırsanız aşağıdaki "Hızlı Şema Kur" betiğini kullanın)

# 4) Servisleri çalıştır
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
python -c "from app.inventory.sync import run; run()"     # GNS3 envanter çek
python - <<'PY'  # Ping check ekle
from app.models.db import SessionLocal
from app.models.core import Device, Check
db=SessionLocal()
for d in db.query(Device).filter(Device.mgmt_ip!=None, Device.enabled==True):
    db.add(Check(device_id=d.id, ctype="ping", params={}, interval_s=10, enabled=True))
db.commit(); db.close()
PY
python -m app.workers.scheduler                          # Toplayıcı/scheduler

# 5) Bak
# http://localhost:8000/metrics
# http://localhost:8000/ui/topology/index.html
# http://localhost:8000/devices  http://localhost:8000/checks

1) Gereksinimler

Python 3.11+

PostgreSQL (önerilir). TimescaleDB şart değil; yoksa gelişmiş agregalar devre dışı kalır.

Alternatif olarak ilk denemede SQLite ile temel akışı test edebilirsiniz. (Bkz: §6.2)

(İsteğe bağlı) Redis (Celery için). Gerekli değil; “hafif scheduler” zaten var.

Windows için: Python kurulumunda “Add Python to PATH” seçeneğini işaretleyin.

2) Projeyi İndir & Sanal Ortam

ZIP’i bilgisayarına indir ve bir klasöre çıkar (örn. C:\netmon veya ~/netmon).

Terminal/Powershell aç → proje klasörüne gir → sanal ortam ve bağımlılıklar:

cd /path/to/netmon

python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt


İlk denemede ağır paketler (ör. prophet, adtk, pyod) derleme sorunları çıkarırsa requirements’tan geçici yorum satırı yapabilirsiniz. Temel ping/HTTP/SNMP akışı onlarsız da çalışır.

3) .env Dosyasını Doldur

Önce şablonu kopyalayın:

cp .env.example .env


Ardından .env içini düzenleyin:

Uzak GNS3 için en kritik iki değişken:

GNS3_URL=http://<UZAK_GNS3_IP>:3080

GNS3_PROJECT=<GNS3’te görünen proje adı>

Veritabanı (önerilen):

DB_URL=postgresql+psycopg2://netmon:netmon@localhost:5432/netmon

İlk testte Redis şart değil:

REDIS_URL=redis://localhost:6379/0 (yoksa kalsın; hafif scheduler kullanacağız)

Portlar:

EXPORTER_PORT=8000 (API & /metrics burada)

Örnek .env (uzak GNS3 ile):

GNS3_URL=http://10.0.0.50:3080
GNS3_PROJECT=CampusLab

DB_URL=postgresql+psycopg2://netmon:netmon@localhost:5432/netmon
REDIS_URL=redis://localhost:6379/0

EXPORTER_PORT=8000


GNS3 proje adını harfiyen doğru yazın (büyük-küçük/boşluk dâhil).

4) Uzak GNS3 Sunucusunu Erişilebilir Yap

Uzak bilgisayarda:

GNS3 Server çalışıyor olmalı (GUI’deki local server da olur).

GUI → Edit → Preferences → Server → Main Server:

Host binding: 0.0.0.0 (veya sunucu IP’si)

“Allow remote connections” işaretli

Güvenlik duvarında 3080/TCP açık.

Kendi bilgisayarından kontrol:

curl http://10.0.0.50:3080/v2/projects


JSON dönüyorsa erişim tamam.

Güvenlik/politika nedeniyle 3080’e doğrudan erişemiyorsanız SSH tüneli kurabilirsiniz:

# macOS/Linux:
ssh -N -L 3080:localhost:3080 user@10.0.0.50
# Windows (PowerShell): OpenSSH yüklüyse aynı komut
# PuTTY: Connection > SSH > Tunnels: Source=3080, Destination=localhost:3080, Add > Open


Bu durumda .env’de GNS3_URL=http://127.0.0.1:3080 yazın.

5) Veritabanı Şeması
5.1 Standart Yol (PostgreSQL + Alembic)
alembic upgrade head


TimescaleDB yoksa CREATE EXTENSION timescaledb adımında hata alabilirsiniz. Sorun değil:

Ya veritabanı süperuser ile bu eklentiyi kurun,

Ya da aşağıdaki “Hızlı Şema Kur (Timescale’siz)” komutunu kullanın.

5.2 Hızlı Şema Kur (Timescale yoksa / SQLite denemesi)

Aşağıdaki komut temel tabloları oluşturur (aggregates/advanced kuralları atlar):

python - <<'PY'
from sqlalchemy import text
from app.models.db import engine
with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS devices (
      id SERIAL PRIMARY KEY, gns3_id VARCHAR(64), name VARCHAR(128) NOT NULL,
      mgmt_ip VARCHAR(64), dtype VARCHAR(32), labels JSONB DEFAULT '{}'::jsonb,
      enabled BOOLEAN DEFAULT TRUE
    );
    CREATE TABLE IF NOT EXISTS links (
      id SERIAL PRIMARY KEY, gns3_id VARCHAR(64),
      a_dev_id INTEGER REFERENCES devices(id),
      b_dev_id INTEGER REFERENCES devices(id),
      a_if VARCHAR(64), b_if VARCHAR(64),
      meta JSONB DEFAULT '{}'::jsonb
    );
    CREATE TABLE IF NOT EXISTS checks (
      id SERIAL PRIMARY KEY, device_id INTEGER REFERENCES devices(id),
      ctype VARCHAR(32), params JSONB DEFAULT '{}'::jsonb,
      interval_s INTEGER NOT NULL, enabled BOOLEAN DEFAULT TRUE
    );
    CREATE TABLE IF NOT EXISTS metrics_raw (
      device_id INTEGER REFERENCES devices(id) NOT NULL,
      check_id INTEGER, ts TIMESTAMPTZ NOT NULL,
      name VARCHAR(64) NOT NULL, value DOUBLE PRECISION NOT NULL,
      labels JSONB DEFAULT '{}'::jsonb
    );
    """))
print("DB hazır (temel tablolar kuruldu).")
PY


SQLite için: .env’de DB_URL=sqlite:///netmon.db yazabilirsiniz. JSONB/TIMESTAMPTZ yoksa SQL’i basitleştirmeniz gerekebilir; ilk denemede Postgres’i tercih edin.

6) Çalıştırma ve GNS3 ile Senkron
6.1 API’yi başlat
uvicorn app.api.main:app --host 0.0.0.0 --port 8000


Sağlık kontrolü: http://localhost:8000/health → {"ok": true}

6.2 GNS3 envanterini çek

Yeni bir terminal (aynı sanal ortam aktif olmalı):

python -c "from app.inventory.sync import run; run()"


Bu işlem, GNS3’teki nodes/links listesini DB’ye yazar.

Doğrula:

http://localhost:8000/devices → cihazlar

http://localhost:8000/topology → JSON

http://localhost:8000/ui/topology/index.html → Topoloji haritası

Önemli: Yönetim IP’si şu kuralla bulunur:

Cihaz adında @ sonrası IP varsa kullanılır: core@10.10.20.1

Yoksa node properties.ip denenir (çoğu node’da boş).

Tavsiye: GNS3’te cihazları ad@IP ile adlandırın.

6.3 Ping check’leri ekle (otomatik)
python - <<'PY'
from app.models.db import SessionLocal
from app.models.core import Device, Check
db=SessionLocal()
for d in db.query(Device).filter(Device.mgmt_ip!=None, Device.enabled==True):
    db.add(Check(device_id=d.id, ctype="ping", params={}, interval_s=10, enabled=True))
db.commit(); db.close()
print("Ping checks eklendi.")
PY

6.4 Toplayıcı / Scheduler (hafif mod)

Redis/Celery olmadan da çalışır:

python -m app.workers.scheduler

6.5 Sonuçları görüntüle

Prometheus metrikleri: http://localhost:8000/metrics
(netmon_device_up, netmon_ping_rtt_ms gibi)

Topoloji Haritası (D3): http://localhost:8000/ui/topology/index.html

(JSON) http://localhost:8000/checks

7) (İsteğe bağlı) HTTP ve SNMP check örnekleri

HTTP:

python - <<'PY'
from app.models.db import SessionLocal
from app.models.core import Check
db=SessionLocal()
db.add(Check(device_id=1, ctype="http",
             params={"url":"http://10.10.20.2:80","expect":200},
             interval_s=30, enabled=True))
db.commit(); db.close()
print("HTTP check eklendi.")
PY


SNMP (v2c):

python - <<'PY'
from app.models.db import SessionLocal
from app.models.core import Check
db=SessionLocal()
db.add(Check(device_id=1, ctype="snmp",
             params={"community":"public"},
             interval_s=30, enabled=True))
db.commit(); db.close()
print("SNMP check eklendi.")
PY


SNMP cihazda açık olmalı, ACL/route izin vermeli. Windows host’larda ICMP Echo güvenlik duvarında açık olmalı.

8) Sık Sorunlar (Checklist)

/v2/projects açılmıyor
GNS3 Server kapalı/yanlış IP/3080 kapalı. Gerekirse SSH tünel kurun.

/devices boş
.env’de GNS3_PROJECT yanlış. Proje GNS3’te açık mı?

Topoloji sayfası boş
Linkler yoksa harita boş görünebilir. GNS3’te kablolar/bağlantılar gerçekten var mı?

/metrics boş
Scheduler çalışıyor mu? Check’ler enabled=true mi? Ping atılabiliyor mu?

alembic upgrade head hata
Timescale yok/izni yok → §5.2 “Hızlı Şema Kur” betiğini kullan.

Ping başarısız
IP yanlış, network izni yok veya Windows ICMP kapalı.

9) Temel Komutlar
# Sanal ortam aç/kapat
source .venv/bin/activate            # Win: .\.venv\Scripts\activate
deactivate

# API
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# Envanter
python -c "from app.inventory.sync import run; run()"

# Scheduler (hafif)
python -m app.workers.scheduler

10) Güvenlik Notları

.env içinde gizli bilgi tutmayın (prod). Demo/lab’da sorun değil.

SNMP’de mümkünse v3 (authPriv) tercih edin (ileri aşamada ekleyin).

RBAC/JWT iskeleti var; prod’da reverse proxy + mTLS önerilir.

11) Yükseltme & Geri Alma

Kod güncelledikten sonra:

Şema değiştiyse: alembic upgrade head

Aksi halde sadece servisleri yeniden başlatın.

Sorun olursa en hızlı geri dönüş:

Önceki DB yedeğini geri yükleyin veya yeni bir DB ile başlatın.

12) SSS

S: Docker yok, kurulum zor mu?
C: Hayır. PostgreSQL önerilir; olmazsa “Hızlı Şema Kur” ile temel tabloları oluşturup ilerleyebilirsiniz.

S: GNS3 projem başka PC’de. Bağlanabilir miyim?
C: Evet. 3080/TCP açık olacak. Olmuyorsa SSH tüneli kurup GNS3_URL=http://127.0.0.1:3080 yapın.

S: Yönetim IP’si nasıl algılanıyor?
C: Cihaz adında ad@IP varsa o IP alınır. En garanti yöntem budur.

13) Ek: Örnek .env Şablonları

Uzak GNS3 + Postgres (önerilen):

GNS3_URL=http://10.0.0.50:3080
GNS3_PROJECT=CampusLab
DB_URL=postgresql+psycopg2://netmon:netmon@localhost:5432/netmon
REDIS_URL=redis://localhost:6379/0
EXPORTER_PORT=8000


Hızlı Yerel Deneme (SQLite + tünel):

GNS3_URL=http://127.0.0.1:3080
GNS3_PROJECT=MyLab
DB_URL=sqlite:///netmon.db
REDIS_URL=memory://
EXPORTER_PORT=8000

14) Runbook Kısaları

Envanter yenile:
python -c "from app.inventory.sync import run; run()"

Ping check ekle (otomatik):
Aşağıdaki bloğu çalıştır:

python - <<'PY'
from app.models.db import SessionLocal
from app.models.core import Device, Check
db=SessionLocal()
for d in db.query(Device).filter(Device.mgmt_ip!=None, Device.enabled==True):
    db.add(Check(device_id=d.id, ctype="ping", params={}, interval_s=10, enabled=True))
db.commit(); db.close()
print("Ping checks eklendi.")
PY


Servisler:

API: uvicorn app.api.main:app --host 0.0.0.0 --port 8000

Scheduler: python -m app.workers.scheduler

Görünüm:

Metrikler: http://localhost:8000/metrics

Topoloji Haritası: http://localhost:8000/ui/topology/index.html

### Detaylı anlatım (Aynı  Cihazda GNS3)
GNS3 ile NetMon aynı makinede çalışınca:

Ağ erişimi sorunu yok (aynı localhost üstünde konuşacaklar).

SSH tüneli ya da firewall açma derdi yok.

Tek yapman gereken .env’de doğru URL ve proje adını vermek.

Adım adım (aynı cihazda GNS3 + NetMon)
1) GNS3 server ayarını kontrol et

GNS3 GUI → Edit → Preferences → Server → Main Server

Host binding: 0.0.0.0 veya 127.0.0.1

Port: 3080 (default)

“Allow remote connections” işaretli olsun (bazen şart olmayabilir ama açık kalsın).

Tarayıcıdan test et:
👉 http://127.0.0.1:3080/v2/projects
JSON dönüyorsa NetMon erişebilecek.

2) .env ayarlarını yap

Aynı cihaz olduğu için sadece 127.0.0.1 yazıyorsun:

GNS3_URL=http://127.0.0.1:3080
GNS3_PROJECT=SeninProjeAdi   # GNS3 GUI’de görünen proje ismi

DB_URL=postgresql+psycopg2://netmon:netmon@localhost:5432/netmon
REDIS_URL=memory://          # Redis şart değil
EXPORTER_PORT=8000


Önemli: GNS3_PROJECT ismini GUI’de “Projects” listesinde nasıl yazıyorsa öyle (boşluk, büyük/küçük harf dahil) girmelisin.

3) Veritabanı

Eğer PostgreSQL kuruluysa onu kullan (önerilen).

Kurulu değilse .env’de DB_URL=sqlite:///netmon.db yazıp SQLite ile test edebilirsin.

Şemayı oluştur:

alembic upgrade head


Timescale kurulu değilse hata verirse README’deki “Hızlı Şema Kur” scriptini kullanabilirsin.

4) API’yi başlat
uvicorn app.api.main:app --host 0.0.0.0 --port 8000


Sağlık kontrol: http://127.0.0.1:8000/health

5) GNS3 envanterini senkronize et
python -c "from app.inventory.sync import run; run()"


Bu komut açık olan GNS3 projesindeki cihazları (nodes/links) veritabanına yazar.

Kontrol et:

http://127.0.0.1:8000/devices

http://127.0.0.1:8000/topology

http://127.0.0.1:8000/ui/topology/index.html

6) Ping check’leri ekle
python - <<'PY'
from app.models.db import SessionLocal
from app.models.core import Device, Check
db=SessionLocal()
for d in db.query(Device).filter(Device.mgmt_ip!=None, Device.enabled==True):
    db.add(Check(device_id=d.id, ctype="ping", params={}, interval_s=10, enabled=True))
db.commit(); db.close()
print("Ping checks eklendi.")
PY

7) Scheduler’ı çalıştır
python -m app.workers.scheduler

8) Sonuçlara bak

Prometheus metrikleri → http://127.0.0.1:8000/metrics

Topoloji haritası → http://127.0.0.1:8000/ui/topology/index.html

Cihaz listesi → http://127.0.0.1:8000/devices