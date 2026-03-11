# Day 2: Multi-Agent Orchestration

## Folder Structure
```text
├── orchestrator/
│   └── planner.py
├── agents/
│   ├── worker_agent.py
│   ├── reflection_agent.py
│   └── validator.py
├── main_d2.py
└── FLOW-DIAGRAM.md
```

## Tasks Completed
- Designed a hierarchical Planner–Executor architecture.
- Implemented DAG-based execution with multiple parallel Worker agents.
- Integrated Reflection and Validator agents to improve and check final answers.
- Generated an execution tree to visualize the agent chain-of-command.

## Code Snippet
```python
# Registering agents onto SingleThreadedAgentRuntime
runtime = SingleThreadedAgentRuntime()
await WorkerAgent.register(runtime, "worker_1", lambda: WorkerAgent("worker_1", model_client))
await PlannerAgent.register(runtime, "planner", lambda: PlannerAgent("planner", model_client, worker_ids))

# Dispatching task to orchestrator
result = await runtime.send_message(UserTask(query=user_query), AgentId("planner", "default"))
```

## Command to Run
```bash
python3 main_d2.py
```

### Output
![Execution Tree](screenshots/planning.png)
