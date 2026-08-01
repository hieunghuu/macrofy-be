from pydantic import BaseModel


class AIStatusResponse(BaseModel):
    configured: bool
    reachable: bool
