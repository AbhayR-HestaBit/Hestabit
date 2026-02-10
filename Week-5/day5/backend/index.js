import express from "express";
import mongoose from "mongoose";
import os from "os";

const app = express();
app.use(express.json());

//middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// connection with db
mongoose.connect(process.env.MONGO_URL)
  .then(() => console.log("Mongo connected"))
  .catch(err => console.error("Mongo error", err));

// Schema
const noteSchema = new mongoose.Schema({
  text: String,
  createdAt: { type: Date, default: Date.now }
});
const Note = mongoose.model("Note", noteSchema);

// -health check
app.get("/health", (req, res) => {
  res.send("OK");
});

// crud opn
app.post("/api/notes", async (req, res) => {
  const note = await Note.create({ text: req.body.text });
  console.log("NOTE_CREATED", note.id);
  res.status(201).json(note);
});

app.get("/api/notes", async (req, res) => {
  const notes = await Note.find().sort({ createdAt: -1 });
  res.json(notes);
});

app.delete("/api/notes/:id", async (req, res) => {
  await Note.findByIdAndDelete(req.params.id);
  console.log("NOTE_DELETED", req.params.id);
  res.sendStatus(204);
});

// Initializing server
app.listen(3000, () => {
  console.log("Backend running on", os.hostname(), ":3000");
});

