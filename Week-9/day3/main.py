import asyncio
import json
import logging

from autogen_core import AgentId, SingleThreadedAgentRuntime

from config import get_settings
from utils.llm_factory import build_text_model_client
from models.day3_messages import Day3Task
from tools.file_agent import FileAgent
from tools.db_agent import DBAgent
from tools.code_executor import CodeAgent
from orchestrator.day3_orchestrator import OrchestratorAgent


async def main() -> None:
    settings = get_settings()

    if getattr(settings, "debug_mode", False):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("autogen_core").setLevel(logging.DEBUG)

    user_query = input("\nEnter your query: ").strip()
    if not user_query:
        print("No query entered. Exiting.")
        return

    model_client = build_text_model_client(settings)
    runtime = SingleThreadedAgentRuntime()

    await FileAgent.register(
        runtime,
        "file_agent",
        lambda: FileAgent(
            "file_agent",
            debug_mode=getattr(settings, "debug_mode", False),
        ),
    )
    await DBAgent.register(
        runtime,
        "db_agent",
        lambda: DBAgent(
            "db_agent",
            debug_mode=getattr(settings, "debug_mode", False),
        ),
    )
    await CodeAgent.register(
        runtime,
        "code_agent",
        lambda: CodeAgent(
            "code_agent",
            model_client=model_client,
            debug_mode=getattr(settings, "debug_mode", False),
        ),
    )
    await OrchestratorAgent.register(
        runtime,
        "orchestrator",
        lambda: OrchestratorAgent(
            "orchestrator",
            model_client=model_client,
            debug_mode=getattr(settings, "debug_mode", False),
        ),
    )

    runtime.start()

    try:
        result = await runtime.send_message(
            Day3Task(query=user_query),
            AgentId("orchestrator", "default"),
        )

        print("\n")
        print("ORCHESTRATOR ROUTE:")
        print("\n")
        print(result.route)

        print("\n")
        print("FILE AGENT:")
        print("\n")
        print(result.file_summary)

        print("\n")
        print("DB AGENT:")
        print("\n")
        print(result.db_summary)
        if result.db_preview:
            print("\nPreview:")
            print(json.dumps(result.db_preview, indent=2))

        print("\n")
        print("CODE AGENT:")
        print("\n")
        print(result.code_agent_answer)

        print("\n")
        print("FINAL ANSWER:")
        print("\n")
        print(result.final_answer)

        if getattr(settings, "debug_mode", False) or result.intent == "code_generation":
            print("\n")
            print("EXECUTION LOG:")
            print("\n")
            print(result.execution_log)
    finally:
        await runtime.stop_when_idle()
        if hasattr(model_client, "close"):
            await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())