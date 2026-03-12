# Day 3: Tool-Calling Agent System (TOOL-CHAIN)

## Architecture Overview
Day 3 implements **tool-calling agents** using AutoGen's `AssistantAgent` with a custom `CustomRouterClient` that enables **"Function Calling Without API"** — injecting tool definitions into the prompt and parsing structured tool calls from LLM text output.

## Smart Orchestration
The system uses a **Smart Router** that classifies the user's query before execution:
```
User Query → LLM Classifier → Select Agents → Execute (Individual or Pipeline)
```

### Routing Logic
| Query Type | Agents Used |
|---|---|
| "Write a python binary search" | `Code_Agent` → `File_Agent` |
| "Read sales.csv and analyze it" | `File_Agent` → `Code_Agent` |
| "Analyze CSV" | `File_Agent` → `DB_Agent` |

## Agents
1. **File_Agent**: `read_file`, `write_file`.
2. **Code_Agent**: `run_python` (Uses `exec()` sandbox).
3. **DB_Agent**: `execute_sql` (SQLite).

## Important Code Snippet
```python
# Tool registration and execution logic
@message_handler
async def handle_tool_call(self, message: ToolCall, ctx: MessageContext) -> ToolResult:
    if message.tool_name == "run_python":
        # Execute code and capture stdout
        result = run_python_code(message.arguments["code"])
        return ToolResult(output=result)
```

## Output
![Day 3 Output](screenshots/Analyze.png)
