import asyncio
from typing import List
from aiohttp import ClientSession, ClientTimeout
import orjson

class Assistant:
    def __init__(self) -> None:
        self.proxy = None
        self.session: ClientSession = None

    async def init(self, proxy=None):
        self.proxy = proxy
        self.session = ClientSession()

    async def context_chat(self, key, context: List, model="gpt-3.5-turbo-16k"):
        headers = {
            "Authorization": "Bearer " + key,
        }
        json_data = {
            "model": model,
            "messages": context,
            "stream": True,
        }
        async with self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
            ssl=False,
            proxy=self.proxy,
        ) as res:
            while not res.content.at_eof():
                chunk = await res.content.readuntil(b"\n\n")
                if chunk == b"\ndata: [DONE]\n":
                    return
                msg = chunk.strip().decode("utf-8")
                if msg.startswith("data: "):
                    data = orjson.loads(msg[6:])
                    token = data["choices"][0]["delta"].get("content", "")
                    yield token
                else:
                    raise Exception(msg)

