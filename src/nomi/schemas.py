from typing import List, Optional
from pydantic import BaseModel, Field

class NomiMessage(BaseModel):
    text: Optional[str] = None
    content: Optional[str] = None
    role: Optional[str] = None

class NomiResponse(BaseModel):
    replyMessage: Optional[NomiMessage] = None
    message: Optional[NomiMessage] = None
    messages: List[NomiMessage] = Field(default_factory=list)

