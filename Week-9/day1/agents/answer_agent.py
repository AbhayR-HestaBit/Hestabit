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


class AnswerAgent(BaseChatAgent):
    """
    Answer Agent
    - Unique role
    - Unique system prompt
    - Memory window = 10
    - Strict job separation
    """

    def __init__(self, name: str, model_client: ChatCompletionClient) -> None:
        super().__init__(name, "Answer-focused agent that produces the final response.")
        self._model_client = model_client
        self._system_messages: list[LLMMessage] = [
            SystemMessage(
                content=(
                    "You are the Answer Agent.\n"
                    "Your only job is to write the final answer for the user.\n"
                    "Write exactly 3 short paragraphs.\n"
                    "Keep the language beginner-friendly.\n"
                    "Do not write dialogue.\n"
                    "Do not use labels like User, Assistant, Chatbot, or Agent.\n"
                    "Use only the provided summary.\n"
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
