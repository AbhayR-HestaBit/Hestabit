const os = require("os");

console.log("OS:", os.type(), os.release());
console.log("Architecture:", process.arch);
console.log("CPU Cores:", os.cpus().length);
console.log("Total Memory (bytes):", os.totalmem());
console.log("System Uptime (seconds):", os.uptime());
console.log("Current Logged User:", os.userInfo().username);
console.log("Node Path:", process.execPath);

