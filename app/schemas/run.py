from typing import Optional

from pydantic import BaseModel
from pydantic import Field

class RunRequest(BaseModel):
    command:str
    tool_name:str

class RunResponse(BaseModel):
    result:str
    tool_name:str


