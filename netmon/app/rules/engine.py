from sqlalchemy import text
from ..models.db import SessionLocal
from ..alerting.slack import send_slack
from ..alerting.actions import start_pcap_for_device

def eval_rules():
    db = SessionLocal()
    q = db.execute(text(
        """
      with last5 as (
        select device_id, name, avg(avg_value) as v
        from metrics_1m_avg
        where bucket >= now() - interval '5 minutes'
        group by device_id, name
      ),
      lastv as (
        select distinct on (device_id,name) device_id, name, avg_value
        from metrics_1m_avg order by device_id,name,bucket desc
      )
      select d.id, d.name,
             coalesce(l5_loss.v,0) as loss5,
             coalesce(lv_http.avg_value,0) as http_up_last
      from devices d
      left join last5 l5_loss on l5_loss.device_id=d.id and l5_loss.name='ping_loss_pct'
      left join lastv lv_http on lv_http.device_id=d.id and lv_http.name='http_up'
    """
    ))
    for did, dname, loss5, http_up_last in q:
        if loss5 > 0:
            send_slack(f":warning: Packet loss on {dname} avg5m={loss5:.1f}%")
        if http_up_last==0 and loss5>0:
            send_slack(f":rotating_light: SITE DOWN {dname} (http_down+loss)")
            start_pcap_for_device(did)
    db.close()