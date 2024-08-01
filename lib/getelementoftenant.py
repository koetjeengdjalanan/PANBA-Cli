from pydantic import BaseModel


class GetElementOfTenant(BaseModel):
    env: dict
    outputFile: str
