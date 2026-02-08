const express = require("express");
const os = require("os");

const app = express();

app.get("/api", (req, res) => {
  res.json({
    message: "Secure response from backend",
    hostname: os.hostname(),
    time: new Date().toISOString()
  });
});

app.listen(3000, () => {
  console.log("Backend running on port 3000");
});

