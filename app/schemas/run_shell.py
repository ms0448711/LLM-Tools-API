from typing import Optional

from pydantic import BaseModel
from pydantic import Field

class RunShellRequest(BaseModel):
    command:str
    session_id:str

class RunShellResponse(BaseModel):
    result:str
    session_id:str
    


