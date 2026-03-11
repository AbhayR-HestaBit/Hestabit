from typing import Any

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import SystemMessage, UserMessage

from orchestrator.planner import ValidationResult, ValidationTask


class ValidatorAgent(RoutedAgent):
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
    async def handle_validation_task(self, message: ValidationTask, ctx: MessageContext) -> ValidationResult:
        self._debug(f"[{self.id.type}] started validation")

        system_prompt = (
            "You are a Validator Agent.\n"
            "Check the draft answer for clarity, completeness, and obvious mistakes.\n"
            "If needed, lightly improve it.\n"
            "Return plain text only.\n"
            "First line must start with: ISSUES:\n"
            "List short issues separated by semicolons, or write NONE.\n"
            "Then a blank line.\n"
            "Then write: FINAL_ANSWER:\n"
            "Then the final validated answer."
        )
        user_prompt = (
            f"Original query:\n{message.original_query}\n\n"
            f"Draft answer:\n{message.draft_answer}\n\n"
            f"Execution tree:\n{message.execution_tree}"
        )

        raw = await self._llm_text(system_prompt, user_prompt)

        issues = []
        final_answer = raw.strip()

        if "FINAL_ANSWER:" in raw:
            before, after = raw.split("FINAL_ANSWER:", 1)
            final_answer = after.strip()
            if "ISSUES:" in before:
                issues_text = before.replace("ISSUES:", "").strip()
                if issues_text and issues_text.upper() != "NONE":
                    issues = [item.strip() for item in issues_text.split(";") if item.strip()]

        self._debug(f"[{self.id.type}] finished validation")

        return ValidationResult(
            is_valid=len(issues) == 0,
            final_answer=final_answer,
            issues=issues,
        )