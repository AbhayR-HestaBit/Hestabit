const express = require("express");
const app = express();

app.get("/api", (req, res) => {
  res.json({
    message: "Response from backend",
    pid: process.pid,
    time: new Date().toISOString()
  });
});

app.listen(3000, () => {
  console.log("Backend running on port 3000");
});
