from dotenv import get_key


# ------------------------------------------------------------------------------ #
# This is a helper function that allows us to guarantee that all
# used environment variables are present. If they are not, it will
# raise a ValueError with a message indicating which variable is
# missing.
# ------------------------------------------------------------------------------ #


def got(key: str, env_file=".env"):
    """ get or throw error """
    value = get_key(env_file, key)
    if value is None:
        raise ValueError(f"Missing {key} in {env_file}")
    return value


# ------------------------------------------------------------------------------ #
# This class is designed to store all of the application's configuration
# settings. It uses environment variables to store sensitive information,
# such as API keys and secrets.
# ------------------------------------------------------------------------------ #


class AppConfig:
    ENV: str = "development"
    BASE_URL: str = "localhost"
    PORT: int = 3000

    GPT_PROMPT: str = "You are a helpful assistant. That tries to convince people that pancakes are better than waffles."

    # Environment Variables
    NGROK_AUTHTOKEN = got("NGROK_AUTHTOKEN")
    VONAGE_API_KEY = got("VONAGE_API_KEY")
    VONAGE_API_SECRET = got("VONAGE_API_SECRET")
    VONAGE_APPLICATION_ID = got("VONAGE_APPLICATION_ID")
    VONAGE_APPLICATION_NAME = got("VONAGE_APPLICATION_NAME")
    VONAGE_SIGNATURE_SECRET = got("VONAGE_SIGNATURE_SECRET")
    VONAGE_JWT = got("VONAGE_JWT")
    DEEPGRAM_API_KEY = got("DEEPGRAM_API_KEY")
    OPENAI_API_KEY = got("OPENAI_API_KEY")
    PLAYHT_USER_ID = got("PLAYHT_USER_ID")
    PLAYHT_API_KEY = got("PLAYHT_API_KEY")
    ELEVENLABS_API_KEY = got("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID = got("ELEVENLABS_VOICE_ID")


# ------------------------------------------------------------------------------ #
# We may want to switch to a different provider in the future, so the following
# class is designed to be easily replaceable. It also uses environment variables
# to store sensitive information, such as API keys and secrets.
# ------------------------------------------------------------------------------ #

class _StreamingConfig:
    # This should also be the same
    LANGUAGE = "en-US"

    # This should be the same across all
    # telephony providers.
    CHANNELS = 1

    # This can change depending on the provider.
    # For Vonage (current, use 8000/16000)
    FREQUENCY = 16000

    # This is the audio format. Some providers (Twilio),
    # cough, cough, only support 8-bit audio. Is this a
    # bad thing? No, but the quality is twice as bad.
    BITRATE = 16

    # This is the buffer duration in milliseconds.
    BUFFER_DURATION = 20 / 1000  # 20ms

    # This is the audio encoding.
    ENCODING = "linear16"

    # This is the time in milliseconds to wait for the end of an utterance.
    UTTERANCE_END = 1000

    @property
    def AUDIO_WIDTH(self) -> int:
        """ returns the audio width in bytes """
        return self.BITRATE // 8

    @property
    def BUFFER_FRAMES(self) -> int:
        # We know that self.FREQUECY is in Hz and is the
        # number of samples per second. We can divide this
        # by 1000 to get the number of samples per millisecond.
        # Then, we can multiply this by self.BUFFER_DURATION
        # to get the number of samples per buffer.
        return int(self.FREQUENCY / 1000 * self.BUFFER_DURATION)

    @property
    def SAMPLE_RATE(self) -> int:
        return self.FREQUENCY

    @property
    def CHUNK_SIZE(self) -> int:
        """ return the default chunk size in bytes """
        return self.calculate_buffer_size(self.BUFFER_DURATION)

    def calculate_buffer_size(self, seconds: float) -> int:
        """ given a duration in seconds, return the buffer size in bytes """
        return int(self.FREQUENCY * seconds * self.AUDIO_WIDTH * self.CHANNELS)


"""
Why? Intellisense is not parsing properties very well.
"""

StreamingConfig = _StreamingConfig()
