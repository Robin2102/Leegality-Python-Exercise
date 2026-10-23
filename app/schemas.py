from pydantic import BaseModel, ConfigDict

class NodeCreate(BaseModel):
    name: str
    
class NodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str