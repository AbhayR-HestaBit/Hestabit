from typing import Any

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import SystemMessage, UserMessage

from orchestrator.planner import ReflectionResult, ReflectionTask


class ReflectionAgent(RoutedAgent):
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

    def _format_worker_results(self, worker_results) -> str:
        parts = []
        for item in worker_results:
            parts.append(
                f"Step {item.step_id}: {item.title}\n"
                f"Worker: {item.worker_name}\n"
                f"Result:\n{item.result}"
            )
        return "\n\n".join(parts)

    @message_handler
    async def handle_reflection_task(self, message: ReflectionTask, ctx: MessageContext) -> ReflectionResult:
        self._debug(f"[{self.id.type}] started reflection")

        system_prompt = (
            "You are a Reflection Agent.\n"
            "Improve the combined worker outputs.\n"
            "Remove duplication, improve clarity, and create one coherent draft answer.\n"
            "Return plain text only.\n"
            "First line must start with: REFLECTION_NOTES:\n"
            "Then a blank line.\n"
            "Then write: IMPROVED_ANSWER:\n"
            "Then the improved answer."
        )
        user_prompt = (
            f"Original query:\n{message.original_query}\n\n"
            f"Worker outputs:\n{self._format_worker_results(message.worker_results)}"
        )

        raw = await self._llm_text(system_prompt, user_prompt)

        reflection_notes = "Reflection completed."
        improved_answer = raw.strip()

        if "IMPROVED_ANSWER:" in raw:
            before, after = raw.split("IMPROVED_ANSWER:", 1)
            improved_answer = after.strip()
            if "REFLECTION_NOTES:" in before:
                reflection_notes = before.replace("REFLECTION_NOTES:", "").strip() or reflection_notes

        self._debug(f"[{self.id.type}] finished reflection")

        return ReflectionResult(
            improved_answer=improved_answer,
            reflection_notes=reflection_notes,
        )