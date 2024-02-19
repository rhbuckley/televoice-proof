import inspect
import json
from typing import Any, AsyncGenerator, Callable, Coroutine, Union
from fastapi import Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketState

from vonage import Client
from vonage.ncco_builder import ConnectEndpoints, Ncco

from const import AppConfig, StreamingConfig
from logging import getLogger

from processing.signals import SignalHandler

from .abstract import Telephony


logger = getLogger(__name__)


class VonageTel(Telephony):
    client: Client

    @classmethod
    def create(cls) -> "VonageTel":
        self = cls()

        self.client = Client(
            # These are for the Vonage API
            key=AppConfig.VONAGE_API_KEY,
            secret=AppConfig.VONAGE_API_SECRET,

            # This is for validating webhooks
            private_key=AppConfig.VONAGE_JWT,
            application_id=AppConfig.VONAGE_APPLICATION_ID,
            signature_secret=AppConfig.VONAGE_SIGNATURE_SECRET,
        )

        return self

    def update_app_urls(self, url: str, method: str = "POST") -> None:
        """
        Update the URL for the app to send data to.

        Args:
            url (str): The URL to send data to.
            method (str): The HTTP method to use for sending data.

        This function will update the application's urls 
            - answer: f'{url}/answer'
            - event: f'{url}/event'
        """
        self.base_url = url
        self.client.application.update_application(
            AppConfig.VONAGE_APPLICATION_ID,
            {
                "name": AppConfig.VONAGE_APPLICATION_NAME,
                "capabilities": {
                    "voice": {
                        "webhooks": {
                            "answer_url": {
                                "address": f"{url}/answer",
                                "http_method": method,
                            },
                            "event_url": {
                                "address": f"{url}/event",
                                "http_method": method,
                            },
                        }
                    }
                }
            }
        )

    def get_phone_number(self) -> str:
        """
        Get a phone number for the application.

        Returns:
            str: The phone number for the application.
        """

        numbers = self.client.numbers.get_account_numbers({
            "application_id": AppConfig.VONAGE_APPLICATION_ID
        })

        try:
            return numbers["numbers"][0]["msisdn"]
        except IndexError:
            raise ValueError("No phone numbers available for this application")

    async def answer(self, request: Request, ws_url: str) -> JSONResponse:
        """
        Answer a call.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: The response to send to the caller.
        """
        # please know that there is an issue in the vonage ncco package
        # I opened a pull request addressing it, but currently, the bitrate
        # will never change because contentType is exported in the final json
        # as `contentType`, whilst the vonage API expects `content-type`
        ct = f"audio/l{StreamingConfig.BITRATE};rate={StreamingConfig.FREQUENCY}"

        ws = ConnectEndpoints.WebsocketEndpoint(
            uri=ws_url,        # type: ignore
            contentType=ct  # type: ignore
        )

        c = Ncco.Connect(endpoint=ws, eventType="synchronous")
        ncco = Ncco.build_ncco(c)
        return JSONResponse(ncco)

    async def websocket(self,
                        ws: WebSocket,
                        on_event: Callable[[str],
                                           Union[Coroutine[Any, Any, Any], None]]
                        ) -> AsyncGenerator[bytes, None]:
        """
        Get media from a WebSocket.

        Args:
            ws (WebSocket): The WebSocket to get media from.
            on_event (Callable[[str], None]): The function to call when a DTMF event is received.

        Returns:
            bytes: The media from the WebSocket.
        """
        try:
            while media := await ws.receive():
                if not SignalHandler.KEEP_RUNNING or media["type"] == "websocket.disconnect":
                    break

                if "bytes" in media:
                    yield media["bytes"]

                elif "text" in media:
                    jmedia = json.loads(media["text"])
                    if jmedia["event"] == "websocket:dtmf":
                        on_event(jmedia["digit"])

        except KeyError as e:
            logger.error(f"Bad Websocket: {e}")

        except Exception as e:
            logger.error(f"Error: {e}")
