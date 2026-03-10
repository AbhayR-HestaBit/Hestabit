import asyncio

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from config import get_settings
from clients.local_hf_client import LocalHFChatClient
from clients.openrouter_client import OpenRouterChatClient
from agents.research_agent import ResearchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.answer_agent import AnswerAgent


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

    user_task = input("\nEnter your query: ").strip()
    if not user_task:
        print("No query entered. Exiting.")
        return

    model_client = build_day_model_client(settings)

    research_agent = ResearchAgent(name="research_agent", model_client=model_client)
    summarizer_agent = SummarizerAgent(name="summarizer_agent", model_client=model_client)
    answer_agent = AnswerAgent(name="answer_agent", model_client=model_client)

    cancellation_token = CancellationToken()

    try:
        research_response = await research_agent.on_messages(
            [TextMessage(content=user_task, source="user")],
            cancellation_token,
        )

        summary_response = await summarizer_agent.on_messages(
            [TextMessage(content=research_response.chat_message.content, source="research_agent")],
            cancellation_token,
        )

        answer_response = await answer_agent.on_messages(
            [TextMessage(content=summary_response.chat_message.content, source="summarizer_agent")],
            cancellation_token,
        )

        print("\n")
        print("USER TASK:")
        print("\n")
        print(user_task)

        print("\n")
        print("RESEARCH AGENT OUTPUT:")
        print("\n")
        print(research_response.chat_message.content)

        print("\n")
        print("SUMMARIZER AGENT OUTPUT:")
        print("\n")
        print(summary_response.chat_message.content)

        print("\n")
        print("ANSWER AGENT OUTPUT:")
        print("\n")
        print(answer_response.chat_message.content)
    finally:
        if hasattr(model_client, "close"):
            await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())