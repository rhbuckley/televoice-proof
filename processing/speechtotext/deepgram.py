import asyncio
from curses import nonl
from typing import Any, AsyncGenerator, Callable, Coroutine, Optional, Union

from processing.signals import SignalHandler
from .abstract import SpeechToText
from const import AppConfig, StreamingConfig
from logging import getLogger

from deepgram import (
    DeepgramClient,
    AsyncLiveClient,
    LiveOptions,
    SpeechStartedResponse,
    LiveResultResponse,
    UtteranceEndResponse,
    MetadataResponse,
    ErrorResponse,
    LiveTranscriptionEvents
)


logger = getLogger(__name__)


class DeepgramSTT(SpeechToText):
    dg: DeepgramClient
    client: AsyncLiveClient
    options: LiveOptions

    PAUSE: bool = False

    @classmethod
    def create(cls) -> "DeepgramSTT":
        self = cls()

        self.dg = DeepgramClient(api_key=AppConfig.DEEPGRAM_API_KEY)
        self.client = self.dg.listen.asynclive.v("1")

        self.options = LiveOptions(
            # model selection
            model="nova-2",

            # language selection
            language=StreamingConfig.LANGUAGE,
            punctuate=True,

            # stream specific config
            encoding=StreamingConfig.ENCODING,
            channels=StreamingConfig.CHANNELS,
            sample_rate=StreamingConfig.FREQUENCY,

            # UtteranceEnd
            interim_results=True,
            utterance_end_ms=str(StreamingConfig.UTTERANCE_END),
            vad_events=True,
        )

        return self

    async def _register_events(self, text_callback: Optional[Callable[[str], Any]] = None, utt_callback: Optional[Callable[[], Any]] = None):
        async def on_message(client, result: LiveResultResponse, **kwargs):
            """ when deepgram sends a message """
            nonlocal text_callback
            if self.PAUSE:
                return

            assert result.channel and result.channel.alternatives
            if result.channel.alternatives[0].transcript and result.speech_final and text_callback:
                await text_callback(result.channel.alternatives[0].transcript)

        async def on_utterance(client, utterance_end: UtteranceEndResponse, **kwargs):
            """ when deepgram says an utterance has ended """
            nonlocal utt_callback
            if self.PAUSE:
                return

            assert utterance_end
            if utt_callback:
                await utt_callback()

        async def on_error(client, error: ErrorResponse, **kwargs):
            """ when deepgram sends an error """
            assert error
            print(error)

        self.client.on(LiveTranscriptionEvents.Transcript, on_message)
        self.client.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance)
        self.client.on(LiveTranscriptionEvents.Error, on_error)

    async def pause(self):
        self.PAUSE = True
        await self.client.finish()

    async def resume(self):
        self.PAUSE = False
        await self.client.start(self.options)

    async def start(self):
        await self.client.start(self.options)
        self.final_result = ''

    async def transcribe(self,
                         audio: AsyncGenerator[bytes, None],
                         callback: Callable[[str], Any],
                         finish: Callable[[], Any]
                         ) -> None:

        try:
            if self.PAUSE:
                return

            await self._register_events(
                text_callback=callback,
                utt_callback=finish
            )

            await self.client.start(self.options)

            async for c in audio:
                if not SignalHandler.KEEP_RUNNING:
                    break
                await self.client.send(c)

            await self.client.finish()

        except asyncio.CancelledError:
            await self.client.finish()
