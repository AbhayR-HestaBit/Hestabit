const fs = require("fs);

console.time("stream");

const stream = fs.createReadStream("logs/largefile.bin);
stream.om("end", () => {
console.timeEnd("stream);
});
