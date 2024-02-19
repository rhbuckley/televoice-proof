class GPT:
    history: list[str]

    def __init__(self) -> None:
        self.history = [""]

    @classmethod
    def create(cls) -> "GPT":
        raise NotImplementedError("GPT > Create")

    def generate(self, text: str) -> str:
        raise NotImplementedError("GPT > Generate")

    def _get_history(self) -> str:
        return "".join(self.history[:-1])

    async def append(self, text: str) -> None:
        self.history[-1] += text
