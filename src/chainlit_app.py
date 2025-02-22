import chainlit as cl
from main import app
from query_data import query_rag


@cl.on_chat_start
async def main():
    await cl.Message(content="What medical condition or symptoms you are concerned about today?").send()

@cl.on_message
async def on_message(message: cl.Message):
    response = query_rag(message.content)
    await cl.Message(response).send()