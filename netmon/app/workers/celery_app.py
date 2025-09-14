import os
from celery import Celery

app = Celery("netmon")
app.conf.broker_url = os.getenv("REDIS_URL","redis://localhost:6379/0")
app.conf.result_backend = None
app.conf.task_acks_late = True
app.conf.worker_max_tasks_per_child = 100