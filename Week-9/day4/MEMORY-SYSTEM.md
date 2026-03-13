# Agent Memory System (Day 4)

## Architecture Overview
The memory system provides agents with both short-term context and long-term persistent knowledge.

## Storage & Retrieval Flow

### How Memory is Stored:
```text
User Message / Assistant Response
      |
      V
[ Session Memory ] (Immediate RAM)
      |
      |---(Append)--> [ SQLite Episodic Store ] (Long-term DB)
      |
      |---(Vectorize)--> [ FAISS Vector Store ] (Similarity Index)
```

### How Memory is Retrieved:
```text
User Query
      |
      |---(Embedded Search)--> [ FAISS Index ]
      |                              |
      |                       [ Relevant Local Context ]
      |                              |
      |---(Query Lookup)------> [ SQLite / Session ]
      |                              |
      |                      [ Historical Details ]
      |                              |
      V                              V
[ Prompt Construction ] <---- [ Combined Context ]
      |
      V
[ LLM Generation ] --> Grounded Final Answer
```

### Short-Term (Session Memory)
- **File**: `memory/session_memory.py`
- **Implementation**: Sliding window of the last 10 messages.

### Long-Term (Persistent Memory)
- **File**: `memory/long_term.db` (SQLite)
- **Implementation**: SQL-based storage for structured episodic history.

### Vector Memory (Similarity Recall)
- **File**: `memory/vector_store.py` (FAISS)
- **Implementation**: Uses `SentenceTransformers` and `FAISS` for semantic similarity search.

## Memory Flow
1. **Search**: Search Vector Store for relevant past facts.
2. **Inject**: Similar context is injected into the system prompt.
3. **Generate**: LLM generates response using recall.

## Important Code Snippet
```python
# FAISS semantic search and context injection logic
query_vector = model.encode([user_query])
D, I = index.search(query_vector, k=3)
recalled_facts = [metadata[idx] for idx in I[0]]

# Inject into system prompt as augmented context
context = "Relevant past facts:\n" + "\n".join(recalled_facts)
```

## Screenshots
![Memory Recall](screenshots/recall.png)



