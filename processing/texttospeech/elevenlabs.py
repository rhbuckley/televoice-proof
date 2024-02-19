from typing import AsyncGenerator
from elevenlabs.client import AsyncElevenLabs

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

    async def speak_stream(self, text_buffer) -> AsyncGenerator[bytes, None]:
        text = "".join([t async for t in text_buffer])
        return await self.speak(text)

    async def close(self):
        pass
