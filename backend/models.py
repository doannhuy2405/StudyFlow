from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str


class UserSignUp(BaseModel):
    username: str
    email: str
    password: str