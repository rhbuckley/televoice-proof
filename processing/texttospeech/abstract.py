from typing import AsyncGenerator, AsyncIterable, AsyncIterator

from const import StreamingConfig


class TextToSpeech:
    @classmethod
    async def create(cls) -> "TextToSpeech":
        raise NotImplementedError("TextToSpeech > Create")

    async def _speak_return(self, it: AsyncIterator[bytes] | AsyncIterable[bytes]) -> AsyncGenerator[bytes, None]:
        buffer = b""
        skipped_headers = False

        async for chunk in it:
            if not skipped_headers:
                skipped_headers = True
                continue

            buffer += chunk
            while len(buffer) > StreamingConfig.CHUNK_SIZE:
                yield buffer[:StreamingConfig.CHUNK_SIZE]
                buffer = buffer[StreamingConfig.CHUNK_SIZE:]

        await self.close()

    async def speak(self, text: str) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError("TextToSpeech > Speak")

    async def speak_stream(self, text_buffer: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError("TextToSpeech > Speak Stream")

    async def close(self):
        raise NotImplementedError("TextToSpeech > Close")
