import re

from pydantic import BaseModel, root_validator
from sqlmodel import Field, SQLModel


class SecretModel(SQLModel, table=True):
    __tablename__ = "secret"  # type: ignore

    secret: bytes
    secret_key_hash: bytes = Field(primary_key=True)


class GenerateInModel(BaseModel):
    secret_phrase: str
    secret: str

    @root_validator
    @classmethod
    def validate_length_and_pattern(cls, values):
        sec_ph = values.get("secret_phrase")
        sec = values.get("secret")
        if sec and not 2 <= len(sec) <= 100:
            raise ValueError("Incorrect secret length")
        if sec_ph and not 2 <= len(sec_ph) <= 20:
            raise ValueError("Incorrect secret_phrase length")
        if not all(i.isspace() or i.isalnum() for i in sec_ph) or not all(
            i.isspace() or i.isalnum() for i in sec
        ):
            raise ValueError("Incorrect symbols")
        return values
