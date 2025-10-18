from pydantic import BaseModel


class CreditCardRequest(BaseModel):
    number: str