from typing import List, Optional

from pydantic import BaseModel, Field


class InventorySelection(BaseModel):
    hosts: Optional[List[str]] = None
    groups: Optional[List[str]] = None


class RunRequest(BaseModel):
    command: Optional[str] = Field(default=None, description="Single command")
    commands: Optional[List[str]] = Field(default=None, description="Multiple commands")
    parser: str = Field(default="raw", description="raw | textfsm | ttp | genie | auto")
    mock: bool = Field(default=True, description="Mock execution instead of real device access")
    inventory: InventorySelection = Field(default_factory=InventorySelection)

    def normalized_commands(self) -> List[str]:
        if self.commands:
            return self.commands
        if self.command:
            return [self.command]
        return []


class RunResponse(BaseModel):
    job_id: str
    status: str
    detail: str
