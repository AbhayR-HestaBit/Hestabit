import asyncio
import logging

from autogen_core import AgentId, SingleThreadedAgentRuntime

from config import get_settings
from clients.local_hf_client import LocalHFChatClient
from clients.openrouter_client import OpenRouterChatClient
from orchestrator.planner import FinalAnswer, PlannerAgent, UserTask
from agents.worker_agent import WorkerAgent
from agents.reflection_agent import ReflectionAgent
from agents.validator import ValidatorAgent


def build_day_model_client(settings):
    if settings.model_provider == "local":
        return LocalHFChatClient(model_path=settings.local_model)

    if settings.model_provider == "api":
        if settings.api_provider == "openrouter":
            if not settings.openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY is missing in .env")
            return OpenRouterChatClient(
                api_key=settings.openrouter_api_key,
                model=settings.openrouter_model,
                base_url=settings.openrouter_base_url,
            )

        if settings.api_provider == "groq":
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is missing in .env")
            return OpenRouterChatClient(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                base_url=settings.groq_base_url,
            )

        raise ValueError(f"Unsupported API_PROVIDER: {settings.api_provider}")

    raise ValueError(f"Unsupported MODEL_PROVIDER: {settings.model_provider}")


async def main() -> None:
    settings = get_settings()

    if settings.debug_mode:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("autogen_core").setLevel(logging.DEBUG)

    user_query = input("\nEnter your query: ").strip()
    if not user_query:
        print("No query entered. Exiting.")
        return

    model_client = build_day_model_client(settings)

    runtime = SingleThreadedAgentRuntime()
    worker_ids = [f"worker_{i}" for i in range(1, settings.max_workers + 1)]

    for worker_id in worker_ids:
        await WorkerAgent.register(
            runtime,
            worker_id,
            lambda wid=worker_id: WorkerAgent(
                wid,
                model_client,
                debug_mode=settings.debug_mode,
            ),
        )

    await ReflectionAgent.register(
        runtime,
        "reflection_agent",
        lambda: ReflectionAgent(
            "reflection_agent",
            model_client,
            debug_mode=settings.debug_mode,
        ),
    )

    await ValidatorAgent.register(
        runtime,
        "validator_agent",
        lambda: ValidatorAgent(
            "validator_agent",
            model_client,
            debug_mode=settings.debug_mode,
        ),
    )

    await PlannerAgent.register(
        runtime,
        "planner",
        lambda: PlannerAgent(
            name="planner",
            model_client=model_client,
            worker_ids=worker_ids,
            reflection_id="reflection_agent",
            validator_id="validator_agent",
            debug_mode=settings.debug_mode,
        ),
    )

    runtime.start()

    try:
        result = await runtime.send_message(
            UserTask(query=user_query),
            AgentId("planner", "default"),
        )
        assert isinstance(result, FinalAnswer)

        print("\n")
        print("DAY 2 FINAL ANSWER:")
        print("\n")
        print(result.answer)

        print("\n")
        print("PLAN STEPS:")
        print("\n")
        for step in result.plan_steps:
            print(step)

        print("\n")
        print("EXECUTION TREE:")
        print("\n")
        print(result.execution_tree)

        print("\n")
        print("VALIDATION ISSUES:")
        print("\n")
        if result.issues:
            for issue in result.issues:
                print(f"- {issue}")
        else:
            print("No issues reported.")
    finally:
        await runtime.stop_when_idle()
        if hasattr(model_client, "close"):
            await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())