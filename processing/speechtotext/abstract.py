from typing import Any, AsyncGenerator


class SpeechToText:
    @classmethod
    async def create(cls) -> "SpeechToText":
        raise NotImplementedError("SpeechToText > Create")

    async def transcribe(self, audio: AsyncGenerator[bytes, None]) -> str:
        raise NotImplementedError("SpeechToText > Transcribe")

    async def transcription_stream(self, audio: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, Any]:
        raise NotImplementedError("SpeechToText > Transcription Stream")
