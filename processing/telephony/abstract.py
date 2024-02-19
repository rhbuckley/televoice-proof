from typing import AsyncGenerator
from fastapi import Request, Response, WebSocket


class Telephony:
    uuid: str  # keep track of the calls

    @classmethod
    async def create(cls) -> "Telephony":
        raise NotImplementedError("Telephony > Create")

    async def answer(self, request: Request) -> Response:
        raise NotImplementedError("Telephony > Answer")

    async def event(self, request: Request) -> Response:
        raise NotImplementedError("Telephony > Event")

    async def websocket(self, websocket: WebSocket) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError("Telephony > Websocket")
