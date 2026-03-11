from dataclasses import dataclass, field
from typing import Any

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from autogen_core.models import SystemMessage, UserMessage


@dataclass
class UserTask:
    query: str


@dataclass
class WorkerTask:
    step_id: int
    title: str
    instruction: str
    original_query: str


@dataclass
class WorkerResult:
    step_id: int
    title: str
    result: str
    worker_name: str


@dataclass
class ReflectionTask:
    original_query: str
    worker_results: list[WorkerResult]


@dataclass
class ReflectionResult:
    improved_answer: str
    reflection_notes: str


@dataclass
class ValidationTask:
    original_query: str
    draft_answer: str
    execution_tree: str


@dataclass
class ValidationResult:
    is_valid: bool
    final_answer: str
    issues: list[str] = field(default_factory=list)


@dataclass
class FinalAnswer:
    answer: str
    execution_tree: str
    plan_steps: list[str]
    issues: list[str] = field(default_factory=list)


class PlannerAgent(RoutedAgent):
    def __init__(
        self,
        name: str,
        model_client: Any,
        worker_ids: list[str],
        reflection_id: str,
        validator_id: str,
        debug_mode: bool = False,
    ) -> None:
        super().__init__(name)
        self._model_client = model_client
        self._worker_ids = worker_ids
        self._reflection_id = reflection_id
        self._validator_id = validator_id
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

    async def _create_plan(self, query: str) -> list[dict[str, str]]:
        system_prompt = (
            "You are a Planner Agent.\n"
            "Break the user query into 2 to 4 executable steps for worker agents.\n"
            "Return plain text only.\n"
            "Format exactly like:\n"
            "1. <title> :: <instruction>\n"
            "2. <title> :: <instruction>"
        )
        user_prompt = f"User query:\n{query}"

        raw = await self._llm_text(system_prompt, user_prompt)
        lines = [line.strip() for line in raw.splitlines() if line.strip()]

        steps: list[dict[str, str]] = []
        for line in lines:
            if "::" in line:
                left, right = line.split("::", 1)
                left = left.strip()
                right = right.strip()

                if ". " in left:
                    _, title = left.split(". ", 1)
                else:
                    title = left

                if title and right:
                    steps.append({"title": title.strip(), "instruction": right.strip()})

        if steps:
            return steps[:4]

        return [
            {
                "title": "Understand the task",
                "instruction": f"Identify the goal, scope, and expected answer for: {query}",
            },
            {
                "title": "Generate key reasoning",
                "instruction": f"Produce the main reasoning points and useful examples for: {query}",
            },
            {
                "title": "Prepare answer material",
                "instruction": f"Create concise answer-ready material for: {query}",
            },
        ]

    @message_handler
    async def handle_user_task(self, message: UserTask, ctx: MessageContext) -> FinalAnswer:
        self._debug("\n[planner] received user task")
        self._debug(f"[planner] query: {message.query}")

        steps = await self._create_plan(message.query)
        self._debug("[planner] generated plan:")
        for i, step in enumerate(steps, start=1):
            self._debug(f"  {i}. {step['title']} -> {step['instruction']}")

        plan_steps = [f"{i+1}. {step['title']}" for i, step in enumerate(steps)]

        worker_results: list[WorkerResult] = []
        tree_lines = [
            f"User Query: {message.query}",
            "└── planner",
        ]

        for idx, step in enumerate(steps, start=1):
            worker_name = self._worker_ids[(idx - 1) % len(self._worker_ids)]
            self._debug(f"\n[planner] sending step {idx} to {worker_name}: {step['title']}")
            tree_lines.append(f"    ├── {worker_name} -> {step['title']}")

            result = await self.send_message(
                WorkerTask(
                    step_id=idx,
                    title=step["title"],
                    instruction=step["instruction"],
                    original_query=message.query,
                ),
                AgentId(worker_name, "default"),
            )

            self._debug(f"[planner] completed step {idx} from {worker_name}")
            self._debug(f"[planner] worker result:\n{result.result}\n")
            worker_results.append(result)

        self._debug(f"[planner] sending combined output to {self._reflection_id}")
        tree_lines.append(f"    ├── {self._reflection_id} -> improve combined answer")

        reflection_result = await self.send_message(
            ReflectionTask(
                original_query=message.query,
                worker_results=worker_results,
            ),
            AgentId(self._reflection_id, "default"),
        )

        self._debug("[planner] reflection completed")
        self._debug(f"[planner] reflection notes: {reflection_result.reflection_notes}")
        self._debug(f"[planner] improved answer:\n{reflection_result.improved_answer}\n")

        self._debug(f"[planner] sending draft to {self._validator_id}")
        tree_lines.append(f"    └── {self._validator_id} -> validate final answer")

        validation_result = await self.send_message(
            ValidationTask(
                original_query=message.query,
                draft_answer=reflection_result.improved_answer,
                execution_tree="\n".join(tree_lines),
            ),
            AgentId(self._validator_id, "default"),
        )

        self._debug("[planner] validation completed")
        self._debug(f"[planner] issues: {validation_result.issues}")
        self._debug("[planner] final validated answer ready\n")

        return FinalAnswer(
            answer=validation_result.final_answer,
            execution_tree="\n".join(tree_lines),
            plan_steps=plan_steps,
            issues=validation_result.issues,
        )