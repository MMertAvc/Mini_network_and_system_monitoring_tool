from pydantic import BaseModel
from typing import Optional, Any, Dict

class DeviceOut(BaseModel):
    id: int
    name: str
    mgmt_ip: Optional[str] = None
    dtype: Optional[str] = None

class CheckOut(BaseModel):
    id: int
    device_id: int
    ctype: str
    params: Dict[str, Any]
    interval_s: int
    enabled: bool