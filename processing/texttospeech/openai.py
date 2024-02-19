import openai
from typing import AsyncGenerator

from const import AppConfig
from .abstract import TextToSpeech


class OpenAITTS(TextToSpeech):
    client: openai.Client

    @classmethod
    def create(cls) -> "OpenAITTS":
        self = cls()

        self.client = openai.Client(
            api_key=AppConfig.OPENAI_API_KEY
        )

        return self

    async def speak(self, text: str) -> AsyncGenerator[bytes, None]:
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="opus",
        )
        
        """
        I'm having a pesky issue with libropus, and the python bindings for it not being
        recognized, going to add elevenlabs support instead.
        """
        
        raise NotImplementedError

        it = await response.aiter_bytes()
        async for data in it:
            yield data
            # yield self.decoder.decode(data)

    async def speak_stream(self, text_buffer: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError
