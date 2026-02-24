import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MemoryTurn:
    role: str
    content: str
    timestamp: str
    sources: List[dict]
    modality: str = "text"


class ConversationMemory:
    # stores and retrieves past conversation history to give the ai memory
    def __init__(self, max_turns: int = 5, storage_dir: str = "src/logs/") -> None:
        self.max_turns = max_turns
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._store: Dict[str, List[MemoryTurn]] = {}

    def _memory_path(self, session_id: str) -> Path:
        return self.storage_dir / f"memory_{session_id}.json"

    def _load_session(self, session_id: str) -> List[MemoryTurn]:
        if session_id in self._store:
            return self._store[session_id]

        path = self._memory_path(session_id)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                turns = [
                    MemoryTurn(
                        role=item.get("role", ""),
                        content=item.get("content", ""),
                        timestamp=item.get("timestamp", ""),
                        sources=item.get("sources", []),
                        modality=item.get("modality", "text"),
                    )
                    for item in data
                ]
                self._store[session_id] = turns
                return turns
            except Exception:
                # If file is corrupted, start fresh for this session
                self._store[session_id] = []
                return self._store[session_id]

        self._store[session_id] = []
        return self._store[session_id]

    def _persist_session(self, session_id: str) -> None:
        turns = self._store.get(session_id, [])
        path = self._memory_path(session_id)
        serializable = [asdict(t) for t in turns]
        path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2))

    def add_turn(
        # saves a new message (either user or ai) into the session history
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[dict]] = None,
        modality: str = "text",
    ) -> None:
        turns = self._load_session(session_id)
        timestamp = datetime.now(timezone.utc).isoformat()

        turn = MemoryTurn(
            role=role,
            content=content,
            timestamp=timestamp,
            sources=sources or [],
            modality=modality,
        )
        turns.append(turn)

        # keep only last max_turns * 2 entries (user + assistant)
        max_entries = self.max_turns * 2
        if len(turns) > max_entries:
            self._store[session_id] = turns[-max_entries:]
        else:
            self._store[session_id] = turns

        self._persist_session(session_id)

    def get_history(self, session_id: str) -> List[dict]:
        turns = self._load_session(session_id)
        max_entries = self.max_turns * 2
        recent = turns[-max_entries:]
        return [asdict(t) for t in recent]

    def format_history_for_prompt(self, session_id: str) -> str:
        # formats the history into a string that the ai can read in its prompt
        turns = self._load_session(session_id)
        if not turns:
            return ""

        max_entries = self.max_turns * 2
        recent = turns[-max_entries:]

        lines: List[str] = ["Previous conversation:"]
        for turn in recent:
            if turn.role.lower() == "user":
                prefix = "User"
            elif turn.role.lower() in {"assistant", "system"}:
                prefix = "Assistant"
            else:
                prefix = turn.role.capitalize() or "User"
            lines.append(f"{prefix}: {turn.content}")

        return "\n".join(lines)

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
        path = self._memory_path(session_id)
        if path.exists():
            path.unlink()

    def list_sessions(self) -> List[str]:
        sessions = set(self._store.keys())
        if self.storage_dir.exists():
            for p in self.storage_dir.glob("memory_*.json"):
                sid = p.stem.replace("memory_", "", 1)
                sessions.add(sid)
        return sorted(sessions)

