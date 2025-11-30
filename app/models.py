from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class Client(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    company: str
    pain_point: str
    status: str = "Lead"
    notes: Optional[str] = None

class Script(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    client_name: str
    title: str
    content: str
    tone: str = "Wolf"
    created_at: datetime = Field(default_factory=datetime.now)
