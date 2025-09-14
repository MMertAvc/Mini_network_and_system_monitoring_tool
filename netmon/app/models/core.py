from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from .db import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    gns3_id = Column(String(64))
    name = Column(String(128), nullable=False)
    mgmt_ip = Column(String(64))
    dtype = Column(String(32))
    labels = Column(JSONB, default=dict)
    enabled = Column(Boolean, default=True)

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    gns3_id = Column(String(64))
    a_dev_id = Column(Integer, ForeignKey("devices.id"))
    b_dev_id = Column(Integer, ForeignKey("devices.id"))
    a_if = Column(String(64))
    b_if = Column(String(64))
    meta = Column(JSONB, default=dict)

class Check(Base):
    __tablename__ = "checks"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    ctype = Column(String(32))
    params = Column(JSONB, default=dict)
    interval_s = Column(Integer)
    enabled = Column(Boolean, default=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    check_id = Column(Integer, ForeignKey("checks.id"))
    rule = Column(String(128))
    state = Column(String(16))
    last_change = Column(TIMESTAMP(timezone=True))