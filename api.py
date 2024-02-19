import ngrok
import logging

from const import AppConfig
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.logger import logger
from fastapi.websockets import WebSocketState

from processing.telephony import VonageTel
from processing.texttospeech import ElevenLabsTTS
from processing.speechtotext import DeepgramSTT
from processing.generate_response import OpenAIGPT


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


class APISettings:
    PORT: int = AppConfig.PORT
    BASE_URL: str = AppConfig.BASE_URL

    NGROK_TOKEN: str = AppConfig.NGROK_AUTHTOKEN
    USE_NGROK: bool = AppConfig.ENV == "development"

    Telephony: VonageTel = VonageTel.create()

    def get_tts(self):
        """ we want to renew the lease on the clients """
        return ElevenLabsTTS.create()

    def get_stt(self):
        """ we want to renew the lease on the clients """
        return DeepgramSTT.create()

    def get_gpt(self):
        return OpenAIGPT.create()

    @property
    def WEBSOCKET_URL(self):
        return f"wss://{self.BASE_URL}/"

    @property
    def API_URL(self):
        return f"https://{self.BASE_URL}/"

    def update_url(self, url: str):
        url = url.lstrip("https://").rstrip("/")
        self.BASE_URL = url
        AppConfig.BASE_URL = url


# ----------------------------------------------------------------------------#
# Application Setup
# ----------------------------------------------------------------------------#
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------#
# API Configuration
# ----------------------------------------------------------------------------#

app = FastAPI()
API = APISettings()

if API.USE_NGROK:
    listener = ngrok.connect(
        addr=f"{API.BASE_URL}:{API.PORT}",
        authtoken=API.NGROK_TOKEN
    )

    # get listener url to update the base url

    print('\n' + ('=' * 80))
    print(f"Tunneled localhost:{API.PORT} -> {API.BASE_URL}")
    print(f"Connected to +{API.Telephony.get_phone_number()}")
    API.update_url(listener.url())
    API.Telephony.update_app_urls(listener.url())
    print(('=' * 80) + '\n')


# ----------------------------------------------------------------------------#
# Websockets
# ----------------------------------------------------------------------------#

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    data = API.Telephony.websocket(
        ws=websocket,
        on_event=lambda e: logger.info(f"Dial : {e}")
    )

    # create the gpt class (for context reset)
    gpt = API.get_gpt()
    stt = API.get_stt()

    async def register_word(word: str):
        await gpt.append(word)

    # create the next step (when user stops speaking)
    async def process_transcript():
        await stt.pause()

        # get the tts client
        tts = API.get_tts()

        # generate response & reset transcript
        response_stream = gpt.generate()

        response_media = await tts.speak_stream(response_stream)

        async for chunk in response_media:
            if not websocket.client_state == WebSocketState.DISCONNECTED:
                await websocket.send_bytes(chunk)

        await stt.resume()

    # start the speech-to-text service
    await stt.transcribe(
        audio=data,
        callback=register_word,
        finish=process_transcript
    )

    if websocket.client_state != WebSocketState.DISCONNECTED:
        await websocket.close()


# ----------------------------------------------------------------------------#
# Webhooks
# ----------------------------------------------------------------------------#

@app.post('/answer')
async def answer(request: Request):
    return await API.Telephony.answer(
        request,
        ws_url=f"wss://{API.BASE_URL}/ws"
    )


@app.post('/event')
async def event(request: Request):
    return Response(status_code=200)


# ----------------------------------------------------------------------------#
# Main
# ----------------------------------------------------------------------------#
if __name__ == "__main__":

    import uvicorn
    logger.debug("Starting server...")

    uvicorn.run(
        app=app,
        host="localhost",
        port=API.PORT,
        ws="websockets",
        log_config="log_conf.yaml",
    )
