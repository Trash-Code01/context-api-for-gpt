from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class Interaction(BaseModel):
    """Tracks a single event (Email, DM, Call) with a timestamp."""
    date: str  # e.g., "2025-11-30 14:30"
    type: str  # e.g., "Cold Email", "DM Reply"
    content: str # e.g., "Sent the pitch deck..."

class Client(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    company: str
    pain_point: str
    status: str = "Lead"
    # This is the new Brain: A list of everything we ever did
    history: List[Interaction] = [] 

class Script(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    client_name: str
    title: str
    content: str
    tone: str = "Wolf"
    created_at: datetime = Field(default_factory=datetime.now)