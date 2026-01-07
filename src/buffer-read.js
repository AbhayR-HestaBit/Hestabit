const fs = require("fs");

console.time("buffer");
fs.readFile("logs/largefile.bin", () =>{
console.timeEnd("buffer");
});
