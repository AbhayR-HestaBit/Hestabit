# Day 5: Capstone — NEXUS AI

## Folder Structure
```text
├── nexus_ai/
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── coder.py
│   │   ├── analyst.py
│   │   ├── critic.py
│   │   ├── optimizer.py
│   │   ├── validator.py
│   │   └── reporter.py
│   ├── main.py
│   └── config.py
├── logs/
├── main_d5.py
└── ARCHITECTURE.md
```

## Tasks Completed
- Built a full autonomous master agent system called NEXUS AI.
- Implemented complex orchestration with 9 specialized agents.
- Integrated dual-memory recall (FAISS + SQLite) and multi-step planning.
- Enabled self-reflection, self-improvement, and failure recovery retry loops.

## Code Snippet
```python
# NEXUS AI Orchestrator workflow
_print_agent_banner("planner", "Analyzing task and building an execution plan")
plan = await self.send_message(message, AgentId("planner", "default"))

# Parallel/Sequential dispatch logic with dependency waves
worker_outputs = await self._execute_in_dependency_waves(
    query=message.query,
    steps=plan.steps,
    memory_context=memory_context,
    task_type=plan.task_type
)
```

## Command to Run
```bash
python3 main_d5.py
```

## Screenshots
![Output](screenshots/output.png)
![Execution](screenshots/execution.png)
![Day 5 Output](screenshots/demo-video.gif)

