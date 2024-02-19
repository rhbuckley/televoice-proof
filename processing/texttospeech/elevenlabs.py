import asyncio
import base64
from email.mime import base
import json
from typing import AsyncGenerator, Generator, Iterator
from elevenlabs import generate
from elevenlabs.client import AsyncElevenLabs
import websockets

from const import AppConfig, StreamingConfig
from .abstract import TextToSpeech


class ElevenLabsTTS(TextToSpeech):
    client: AsyncElevenLabs

    @classmethod
    def create(cls) -> "ElevenLabsTTS":
        self = cls()
        self.client = AsyncElevenLabs(api_key=AppConfig.ELEVENLABS_API_KEY)
        return self

    async def speak(self, text: str) -> AsyncGenerator[bytes, None]:

        assert StreamingConfig.SAMPLE_RATE == 16000, "ElevenLabs only supports 16kHz sample rate"

        res = self.client.text_to_speech.convert_as_stream(
            voice_id=AppConfig.ELEVENLABS_VOICE_ID,
            text=text,
            output_format="pcm_16000",
        )

        return self._speak_return(res)

    async def speak_stream(self, text_buffer: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        async def text_chunker(chunks):
            """Split text into chunks, ensuring to not break sentences."""
            splitters = (".", ",", "?", "!", ";", ":", "—",
                         "-", "(", ")", "[", "]", "}", " ")
            buffer = ""

            async for text in chunks:
                if buffer.endswith(splitters):
                    yield buffer + " "
                    buffer = text
                elif text.startswith(splitters):
                    yield buffer + text[0] + " "
                    buffer = text[1:]
                else:
                    buffer += text

            if buffer:
                yield buffer + " "

        """Send text to ElevenLabs API and stream the returned audio."""
        uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{AppConfig.ELEVENLABS_VOICE_ID}/stream-input"

        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({
                "text": " ",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                "xi_api_key": AppConfig.ELEVENLABS_API_KEY,
            }))

            async def listen():
                """Listen to the websocket for audio data and stream it."""
                try:
                    while message := await websocket.recv():
                        data = json.loads(message)

                        if data.get("audio"):
                            yield base64.b64decode(data["audio"])

                        elif data.get('isFinal'):
                            break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection Closed with ElevenLabs")

            async for text in text_chunker(text_buffer):
                await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

            await websocket.send(json.dumps({"text": ""}))

        return listen()

    async def close(self):
        pass
