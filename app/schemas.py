from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NodeName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]

class NodeCreate(BaseModel):
    name: NodeName
    
class NodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    
class EdgeCreate(BaseModel):
    source: NodeName
    destination: NodeName
    latency: float = Field(gt=0, allow_inf_nan=False)
    
class EdgeOut(BaseModel):
    id: str
    source: str
    destination: str
    latency: float