# The Televoice Project

This has been a weekend project over President's Day weekend '24, and was inspired by another one of my projects.
I started this project with a very different approach, and have used multiple VoiceAPIs, and text-to-speech providers.

## Control Flow

![Voice Control Flow Image](/docs/televoice-proof.png)

## Demo

## Installation Instructions

### Install required dependencies

Ensure that you first have all of the required dependencies installed,
which relate to fastapi, ngrok, etc.

```bash
pip install -r requirements.txt
```

### Run the API

You can run the API by calling `api.py`.

```bash
python3 api.py
```

#### A Note on NGROK

I have used NGROK in this project, as it has allowed me to quickly develop
and establish a tunnel from my development environment to outside IDEs. This
is not required, but will need some editing to change.

#### Adding Environment Variables

I have provided an empty environment file template below. Copy and paste this into `.env`,
and begin pasting in your API keys.

```bash
NGROK_AUTHTOKEN=""

# telephon
VONAGE_API_KEY=""
VONAGE_API_SECRET=""
VONAGE_APPLICATION_ID=""
VONAGE_APPLICATION_NAME=""
VONAGE_SIGNATURE_SECRET=""
VONAGE_JWT=""

# speech to tex
DEEPGRAM_API_KEY=""

# gpt to generate a respons
OPENAI_API_KEY=""

# text to speech
PLAYHT_USER_ID=""
PLAYHT_API_KEY=""

ELEVENLABS_VOICE_ID=""
ELEVENLABS_API_KEY=""
```

### Project Setup

This project has been setup with three main components.

#### `api.py`

This is where our FastAPI instance lives. This is also the entrypoint to this program.

#### `const.py`

This is where all project related settings go.

#### `processing`

This is where all files related to processing go. This contains four main modules.

1. `generate_response` - This is where we generate the response to send to the client.
2. `speechtotext` - This is where we convert speech to text
3. `texttospeech` - This is where we convert text to speech
4. `telephony` - This provides a class that allows us to change Telephony providers

All modules in this folder are object oriented. In each of the modules, I have added an
`abstract.py`, where I have defined the base class. In each of the files inside each module,
the Abstract class is implemented, and then finally imported in `api.py`. To swap modules,
look at `APISettings` in `api.py`.

## Caveats

This was a fun project, however, I was not thrilled with some of the things that I ran into.
First of all, I started by using the Telnyx Voice API. The Telnyx documentation was great, but
I could not get any high-quality audio without establishing a RTC connection. I also tried twilio,
and found the same issue. Vonage, on the other hand, provided twice as good audio over websockets,
so that was nice to see.

If I had more time I would implement more, and on a local machine with a gpu. This would cut down on
the latency. For example, if I used openai/whisper, instead of Deepgram, I have a feeling I could cut
down on the speech processing time.

Finally, context seems to be important to streaming text-to-speech, so we need to wait for the chat completion
to finish before generating audio. I think I would change this to have a sliding window of context to feed to
the text-to-speech service, but am not sure how I would do this yet.

Also, as seen in the `texttospeech/open_ai.py` file, I was not able to get the opus bindings to work for python,
and was not able to implement openai text to speech (I could get it to work, but it's Monday and time for schoolwork).
