from sqlmodel import SQLModel


class Message(SQLModel):
    msg: str
