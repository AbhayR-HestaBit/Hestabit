import { useState, useEffect } from "react";
import "./App.css";

export default function App() {
  const [notes, setNotes] = useState([]);
  const [text, setText] = useState("");

  const fetchNotes = async () => {
    const res = await fetch("/api/notes");
    const data = await res.json();
    setNotes(data);
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const createNote = async () => {
    if (!text.trim()) return;

    await fetch("/api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    setText("");
    fetchNotes();
  };

  const deleteNote = async (id) => {
    await fetch(`/api/notes/${id}`, {
      method: "DELETE",
    });
    fetchNotes();
  };

return (
  <main className="app">
    <section className="container">
      
      <header className="app-header">
        <h1 className="app-title">Notes</h1>
        <p className="app-subtitle">
        </p>
      </header>

      <section className="note-creator" aria-label="Create new note">
        <div className="input-group">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Write a note..."
            aria-label="Note text"
          />
          <button onClick={createNote}>
            Add Note
          </button>
        </div>
      </section>

      <section className="notes-section" aria-label="Notes list">
        {notes.length === 0 ? (
          <div className="empty">
            No notes yet.
          </div>
        ) : (
          <ul className="notes">
            {notes.map((note) => (
              <li key={note._id} className="note-card">
                <p>{note.text}</p>
                <button
                  onClick={() => deleteNote(note._id)}
                  aria-label="Delete note"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

    </section>
  </main>
);
}
