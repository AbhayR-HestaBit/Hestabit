const {Worker} = require("worker_threads");

console.log("Main thread PID:", process.pid);

const worker = new Worker("./worker-task.js");

console.time("worker-task");

worker.postMessage(5e8);

worker.on("message", (result) => {
console.timeEnd("worker-task");
console.log("Result:", result);
worker.terminate();
});

