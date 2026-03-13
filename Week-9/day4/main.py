import asyncio
import logging

from autogen_core.models import SystemMessage, UserMessage

from config import get_settings
from memory.session_memory import SessionMemory
from memory.vector_store import FaissVectorStore
from utils.llm_factory import build_text_model_client


def build_memory_context(
    recent_context: str,
    fact_context: str,
    vector_context: str,
) -> str:
    return (
        "Relevant memory context:\n\n"
        f"Short-term session memory:\n{recent_context}\n\n"
        f"Long-term SQLite facts:\n{fact_context}\n\n"
        f"Vector recall:\n{vector_context}\n"
    )


async def main() -> None:
    settings = get_settings()

    if getattr(settings, "debug_mode", False):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("autogen_core").setLevel(logging.DEBUG)

    model_client = build_text_model_client(settings)

    session_memory = SessionMemory(db_path="memory/long_term.db", max_turns=10)
    vector_store = FaissVectorStore(
        index_path="memory/vector.index",
        metadata_path="memory/vector_metadata.pkl",
        dim=1024,
    )

    print("\nDAY 4 MEMORY SYSTEM READY")
    print("Type 'exit' to quit.\n")

    try:
        while True:
            user_query = input("You: ").strip()
            if not user_query:
                continue
            if user_query.lower() in {"exit", "quit"}:
                break

            fact_hits = session_memory.search_facts(user_query, limit=5)
            vector_hits = vector_store.search(user_query, k=3)

            recent_context = session_memory.format_recent_context()
            fact_context = session_memory.format_fact_results(fact_hits)
            vector_context = vector_store.format_search_results(vector_hits)

            memory_context = build_memory_context(
                recent_context=recent_context,
                fact_context=fact_context,
                vector_context=vector_context,
            )

            system_prompt = (
                "You are a memory-aware assistant. "
                "Use the retrieved memory context when it is relevant. "
                "Do not invent past context. "
                "Answer naturally and clearly."
            )

            user_prompt = (
                f"{memory_context}\n\n"
                f"Current user query:\n{user_query}"
            )

            result = await model_client.create(
                [
                    SystemMessage(content=system_prompt),
                    UserMessage(content=user_prompt, source="user"),
                ]
            )
            assistant_answer = str(result.content).strip()

            print("\n")
            print("MEMORY RETRIEVAL:")
            print("\n")
            print(memory_context)

            print("\n")
            print("ASSISTANT ANSWER:")
            print("\n")
            print(assistant_answer)
            print()

            session_memory.add_turn("user", user_query)
            session_memory.add_turn("assistant", assistant_answer)

            user_facts = session_memory.extract_important_facts(user_query)
            assistant_facts = session_memory.extract_important_facts(assistant_answer)
            session_memory.store_facts(user_facts + assistant_facts)

            vector_store.add_text(user_query, {"role": "user"})
            vector_store.add_text(assistant_answer, {"role": "assistant"})

    finally:
        if hasattr(model_client, "close"):
            await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())