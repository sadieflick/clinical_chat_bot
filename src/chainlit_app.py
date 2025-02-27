import chainlit as cl
import asyncio
from rag_processing import getResponse



@cl.on_chat_start
async def main():
    await cl.Message(content="What medical condition or symptoms you are concerned about today?").send()

@cl.on_message
async def on_message(message: cl.Message):
    response = await cl.make_async(getResponse)(message.content)
    await cl.Message(response).send()

