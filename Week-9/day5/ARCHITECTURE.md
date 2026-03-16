# NEXUS AI — Architecture

## Architecture Diagram

```text
                        ┌─────────────────────────────────┐
                        │         USER TASK INPUT         │
                        └────────────────┬────────────────┘
                                         │
                        ┌────────────────▼────────────────┐
                        │       MEMORY RECALL (FAISS)     │
                        │  Vector search → inject context │
                        └────────────────┬────────────────┘
                                         │
                        ┌────────────────▼────────────────┐
                        │         ORCHESTRATOR            │
                        │  Master coordination & tracing  │
                        │  Failure recovery / Fallbacks   │
                        └──┬─────────────┬─────────────┬──┘
                           │             │             │
               ┌───────────▼──┐  ┌───────▼───────┐  ┌──▼──────────────┐
               │   PLANNER    │  │  COMPLETION   │  │   TOOLSMITH     │
               │  Multi-step  │  │   CHECKER     │  │  Just-in-time   │
               │  graph builds│  │ Task Contract │  │  tool creation  │
               └───────────┬──┘  └───────┬───────┘  └──┬──────────────┘
                           │             │             │
               ┌───────────▼─────────────▼─────────────▼──────────────┐
               │              EXECUTION       (Workers)               │
               │      [Researcher]   [Coder]   [Analyst]              │
               │      Parallel dispatch based on dependencies         │
               └─────────────────────────┬────────────────────────────┘
                                         │
               ┌─────────────────────────▼────────────────────────────┐
               │               CRITIC (Self-Reflection)               │
               │      Identifies risks, gaps, and logical flaws       │
               └─────────────────────────┬────────────────────────────┘
                                         │
               ┌─────────────────────────▼────────────────────────────┐
               │             OPTIMIZER (Self-Improvement)             │
               │      Synthesizes worker outputs + addresses gaps     │
               └─────────────────────────┬────────────────────────────┘
                                         │
               ┌─────────────────────────▼────────────────────────────┐
               │              VALIDATOR (Audit & Score)               │
               │      Grounding, Artifact verified, Depth check       │
               └─────────────────────────┬────────────────────────────┘
                                         │
               ┌─────────────────────────▼────────────────────────────┐
               │              REPORTER (Finalization)                 │
               │      Artifact Manifest + Full execution trace        │
               └──────────────────────────────────────────────────────┘
```

---

## Agent Roles
| Agent | Role | Tools |
|-------|------|-------|
| Orchestrator | Master coordinator, routes and monitors | None (decision only) |
| Planner | Multi-step task decomposition (Directed Acyclic Graph) | `create_plan` |
| Completion Checker | Extracts "Fulfillment Contract" (depth, sections, artifacts) | `define_contract`, `analyze_fulfillment` |
| Toolsmith | JIT Tool creation for missing capabilities | `build_python_tool` |
| Researcher | Context gathering, file reading, web scraping | `web_search`, `read_file`, `list_files` |
| Coder | Implementation, execution, repair, analysis | `run_code`, `write_file`, `csv_summary` |
| Analyst | Logical review, business strategy, SQL | `run_code`, `execute_sql` |
| Critic | Self-reflection, quality auditing | None |
| Optimizer | Draft synthesis, structured refinement | None |
| Validator | Score-based verification (Artifacts, Depth, Grounding) | `verify_file`, `run_code` |
| Reporter | Manifest generation, trace reporting | `save_report` |

---

## Memory System

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Short-term | Session (Python list) | Sliding window of 10 messages |
| Long-term | SQLite (`memory/long_term.db`) | Persistent episodic memory |
| Vector | FAISS + SentenceTransformers | Semantic similarity recall |

---

## File Structure

```
Week-9/
├── nexus_ai/
│   ├── config.py           
│   ├── agents.py           
│   ├── orchestrator.py     
│   ├── tools.py            
│   └── logger.py           
├── memory/
│   ├── manager.py          
│   ├── vector_store.py     
│   ├── session_memory.py   
│   ├── long_term.db        
│   ├── faiss_index.bin     
│   └── metadata.json       
├── tools/
│   ├── file_agent.py       
│   ├── code_executor.py    
│   └── db_agent.py         
├── logs/
│   ├── nexus_ai.log        
│   └── trace_*.jsonl       
├── output/                 
├── data/
│   └── sales.csv           
├── ARCHITECTURE.md         
└── FINAL-REPORT.md         
```
## Internal Task Handling & Flow

1. **Planning & Contracting**: The **Planner** decomposes the query into a DAG of steps. Simultaneously, the **Completion Checker** defines a **Fulfillment Contract** that specifies exactly what "done" looks like (e.g., minimum character depth, specific markdown headers, required file artifacts).
2. **Execution Waves**: Steps are executed in **Waves** based on dependencies. Independent steps run in parallel, while implementation steps wait for their prerequisites.
3. **JIT Tool Generation (Toolsmithing)**: If a task requires a capability not present in the base tools, the **Toolsmith** generates a scoped Python helper tool on-the-fly.
4. **Continuous Refinement**: The **Critic** identifies logical gaps, and the **Optimizer** synthesizes worker results into a cohesive final draft.
5. **Multi-Stage Validation**: The **Validator** audits structural integrity (contract), functional correctness (execution), and substantive grounding.
6. **Failure Recovery**: Includes **Fallback Owners** (handoffs between agents), **Targeted Retries** (re-running only failed parts), and **Persistence Fallback** (Orchestrator-level file saving).

## Orchestration Logic

```python
# Orchestration Loop (Wave-based)
async def handle_task(self, message: NexusTask, ctx: MessageContext):
    # Plan & Contract
    plan = await self.send_message(message, AgentId("planner"))
    contract = await self.send_message(ContractRequest(message.query), AgentId("completion_checker"))

    # Parallel Execution Waves
    worker_outputs = await self._execute_in_dependency_waves(plan.steps)

    # Quality Loop
    critique = await self.send_message(CritiqueInput(worker_outputs), AgentId("critic"))
    optimizer = await self.send_message(OptimizationInput(critique), AgentId("optimizer"))

    # Final Validation against Contract
    completion = await self.send_message(CompletionCheckInput(optimizer.draft, contract), AgentId("completion_checker"))
    validator = await self.send_message(ValidationInput(completion), AgentId("validator"))

    return await self._report(validator)
```

## Output
![Day 5 Output](screenshots/demo-video.gif)