from pydantic import BaseModel, Field
from datetime import datetime

class GreyhoundMessageStage(BaseModel):

    destination: str
    inputs: dict = Field(default_factory=dict)
    outputs: dict = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)

class GreyhoundMessageMetadata(BaseModel):

    correlation_id: str
    message_id: str
    timestamp: datetime | None = None
    priority: int | None = None
    retry_count: int | None = None
    error_message: str | None = None
    custom_headers: dict = Field(default_factory=dict)

class GreyhoundMessageRoot(BaseModel):

    event_type: str
    is_dry_run: bool = False
    stages: list[GreyhoundMessageStage] = Field(default_factory=list)
    payload: dict
    metadata: GreyhoundMessageMetadata = Field(default_factory=GreyhoundMessageMetadata) 
