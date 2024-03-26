from typing import List

from pydantic import BaseModel
from pydantic import Field

class CleanSessionRequest(BaseModel):
    prefix:str


class CleanSessionResponse(BaseModel):
    result:List[str]


