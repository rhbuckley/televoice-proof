import openai
from typing import AsyncGenerator, Optional

from .abstract import GPT
from const import AppConfig


class OpenAIGPT(GPT):
    client: openai.Client

    @classmethod
    def create(cls) -> "OpenAIGPT":
        self = cls()

        self.client = openai.Client(
            api_key=AppConfig.OPENAI_API_KEY
        )

        return self

    async def generate(self, text: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not text:
            text = self.history.pop()

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": AppConfig.GPT_PROMPT},
                {"role": "system", "content": "Conversation Context: " +
                    self._get_history()},
                {"role": "user", "content": text}
            ],
            stream=True
        )

        self.history.append(f"User: {text}")
        self.history.append("GPT: ")

        print(f"\n>>> {text}\n<<< ", end="")
        for chunk in response:
            if chunk.choices[0].delta.content:
                self.history[-1] += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")
                yield chunk.choices[0].delta.content

        print("\n")
        # just a blank line in case the .append method is used
        self.history.append("")
