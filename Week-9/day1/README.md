# Day 1: Agent Foundations & Message-Based Communication

## Folder Structure
```text
├── agents/
│   ├── research_agent.py
│   ├── summarizer_agent.py
│   └── answer_agent.py
├── main_d1.py
└── AGENT-FUNDAMENTALS.md
```

## Tasks Completed
- Defined unique roles and system prompts for Research, Summarizer, and Answer agents.
- Implemented a strict job separation with a memory window of 10.
- Built the ReAct pattern loop: Research Agent -> Summarizer Agent -> Answer Agent.
- Verified message protocol systems using AutoGen's `TextMessage`.

## Important Code Snippet
```python
# Sequential message passing between specialized agents
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
```

## Command to Run
```bash
python3 main_d1.py
```

### Output
![Day 1 Output](screenshots/main.png)
