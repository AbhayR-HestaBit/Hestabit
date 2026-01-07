const fs = require("fs");

console.time("buffer");
fs.readfile("logs/largefile.bin", () =>{
console.timeEnd("buffer");
});
