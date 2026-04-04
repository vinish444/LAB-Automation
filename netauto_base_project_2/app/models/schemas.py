from typing import List, Optional

from pydantic import BaseModel, Field


class DeviceSelection(BaseModel):
    hosts: Optional[List[str]] = Field(default=None, description="Subset of hosts from Nornir inventory")
    groups: Optional[List[str]] = Field(default=None, description="Inventory groups to filter")


class RunRequest(BaseModel):
    command: str = Field(..., examples=["show version"])
    commands: Optional[List[str]] = Field(default=None, description="Optional multiple commands")
    parser: str = Field(default="raw", examples=["raw", "textfsm"])
    use_queue: bool = True
    inventory: Optional[DeviceSelection] = None
    mock: bool = True


class RunResponse(BaseModel):
    job_id: str
    status: str
    detail: str
