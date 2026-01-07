const fs = require("fs");

console.time("stream");

const stream = fs.createReadStream("logs/largefile.bin");
stream.on("end", () => {
console.timeEnd("stream");
});

