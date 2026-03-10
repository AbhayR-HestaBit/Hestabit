from typing import Sequence

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import BaseChatMessage, TextMessage
from autogen_core import CancellationToken
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
)


class SummarizerAgent(BaseChatAgent):
    """
    Summarizer Agent
    - Unique role
    - Unique system prompt
    - Memory window = 10
    - Strict job separation
    """

    def __init__(self, name: str, model_client: ChatCompletionClient) -> None:
        super().__init__(name, "Summarization-focused agent that compresses research notes.")
        self._model_client = model_client
        self._system_messages: list[LLMMessage] = [
            SystemMessage(
                content=(
                    "You are the Summarizer Agent.\n"
                    "Your only job is to summarize research notes.\n"
                    "Return exactly 3 short bullet points.\n"
                    "Do not add new facts.\n"
                    "Do not write dialogue.\n"
                    "Do not write a final answer.\n"
                    "Do not use labels like User, Assistant, Chatbot, or Agent.\n"
                    "Strict role isolation."
                )
            )
        ]
        self._memory: list[LLMMessage] = []
        self._memory_window = 10

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)

    def _trim_memory(self) -> None:
        self._memory = self._memory[-self._memory_window :]

    async def on_messages(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token: CancellationToken,
    ) -> Response:
        for message in messages:
            self._memory.append(
                UserMessage(content=message.to_text(), source=message.source)
            )
        self._trim_memory()

        result = await self._model_client.create(
            messages=self._system_messages + self._memory,
            cancellation_token=cancellation_token,
        )

        assert isinstance(result.content, str)

        self._memory.append(
            AssistantMessage(content=result.content, source=self.name)
        )
        self._trim_memory()

        return Response(
            chat_message=TextMessage(content=result.content, source=self.name)
        )

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        self._memory.clear()
