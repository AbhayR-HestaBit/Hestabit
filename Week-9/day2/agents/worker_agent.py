from typing import Any

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import SystemMessage, UserMessage

from orchestrator.planner import WorkerResult, WorkerTask


class WorkerAgent(RoutedAgent):
    def __init__(self, name: str, model_client: Any, debug_mode: bool = False) -> None:
        super().__init__(name)
        self._model_client = model_client
        self._debug_mode = debug_mode

    def _debug(self, text: str) -> None:
        if self._debug_mode:
            print(text)

    async def _llm_text(self, system_prompt: str, user_prompt: str) -> str:
        result = await self._model_client.create(
            [
                SystemMessage(content=system_prompt),
                UserMessage(content=user_prompt, source=self.id.type),
            ]
        )
        return str(result.content).strip()

    @message_handler
    async def handle_worker_task(self, message: WorkerTask, ctx: MessageContext) -> WorkerResult:
        self._debug(f"[{self.id.type}] started step {message.step_id}: {message.title}")

        system_prompt = (
            "You are a Worker Agent.\n"
            "Execute only the assigned step.\n"
            "Be concise and useful.\n"
            "Do not write the final answer.\n"
            "Do not perform reflection or validation.\n"
            "Return only the step result."
        )
        user_prompt = (
            f"Original query:\n{message.original_query}\n\n"
            f"Step title: {message.title}\n"
            f"Step instruction: {message.instruction}"
        )

        text = await self._llm_text(system_prompt, user_prompt)

        self._debug(f"[{self.id.type}] finished step {message.step_id}")

        return WorkerResult(
            step_id=message.step_id,
            title=message.title,
            result=text,
            worker_name=self.id.type,
        )