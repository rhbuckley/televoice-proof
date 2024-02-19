from typing import AsyncGenerator, AsyncIterable

import pyht

from const import AppConfig, StreamingConfig
from .abstract import TextToSpeech


class PlayHTTTS(TextToSpeech):
    client: pyht.AsyncClient
    options: pyht.TTSOptions

    @classmethod
    def create(cls) -> "PlayHTTTS":
        self = cls()

        self.client = pyht.AsyncClient(
            AppConfig.PLAYHT_USER_ID,
            AppConfig.PLAYHT_API_KEY
        )

        # configure your stream
        self.options = pyht.TTSOptions(
            # this voice id can be one of our prebuilt voices or your own voice clone id, refer to the`listVoices()` method for a list of supported voices.
            # voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json",
            voice="s3://peregrine-voices/oliver_narrative2_parrot_saad/manifest.json",
            # voice="en-US-JasonNeural",
            # voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json",

            # you can pass any value between 8000 and 48000, 24000 is default
            sample_rate=StreamingConfig.FREQUENCY,

            # the generated audio encoding, supports 'raw' | 'mp3' | 'wav' | 'ogg' | 'flac' | 'mulaw'
            format=pyht.Format.FORMAT_WAV,

            # playback rate of generated speech
            speed=1,
        )

        # this is what format=wav returns
        # nchannels=1, sampwidth=2, framerate=8000, nframes=2147483647, comptype='NONE', compname='not compressed'

        return self

    def speak(self, text: str) -> AsyncGenerator[bytes, None]:
        """ This streams text to the PlayHT API and returns the audio data. """

        response = self.client.tts(
            text=text,
            voice_engine="PlayHT2.0-turbo",
            options=self.options
        )

        return self._speak_return(response)

    def speak_stream(self, text_buffer: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """ This streams text buffer to the PlayHT API and returns the audio data. """

        response = self.client.stream_tts_input(
            text_stream=text_buffer,
            voice_engine="PlayHT2.0-turbo",
            options=self.options
        )

        return self._speak_return(response)

    async def close(self):
        await self.client.close()
