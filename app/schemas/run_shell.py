from typing import Optional

from pydantic import BaseModel
from pydantic import Field

class RunShellRequest(BaseModel):
    command:str
    session_id:str
    pane_id:int

class RunShellResponse(BaseModel):
    result:str
    session_id:str
    pane_id:int
    


