from pydantic import BaseModel
from chainlit.message import Message


class RequestBody(BaseModel, Message):
    pass