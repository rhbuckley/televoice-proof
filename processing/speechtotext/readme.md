## Usage

We are currently using the Deepgram Realtime Transcription API. OpenAI Whisper, does not currently support realtime streaming without breaking up media into chunks.

### Abstract

The abstract class for these speech-to-text wrappers contains the following methods:

-   `transcribe(audio_stream)` This waits for the whole audio stream to be parsed (until an UtteranceEnd), and then returns.

-   `transcription_stream(audio_stream)` This returns an asynchronous generator that iterates until an UtteranceEnd
