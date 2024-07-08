from pydantic import BaseModel, ConfigDict


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    model_config = ConfigDict(extra="forbid")
