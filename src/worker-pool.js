const { Worker } = require("worker_threads");
const os = require("os");
const WORKER_COUNT = Math.min(4, os.cpus().length);
const workers = [];
const queue = [];

let workerIndex = 0;

function createWorker() {
const worker = new Worker("./worker-task.js");

worker.on("message", (result) => {
worker.busy = false;
if (queue.length >0){
const job = queue.shift();
worker.busy = true;
worker.postMessage(job.iterations);
job.resolve(result);
}
});

worker.busy = false;
return worker;
}

for  (let i=0; i< WORKER_COUNT; i++) {
workers.push(createWorker());
}

function runJob(iterations) {
return new Promise((resolve) => {
const availableWorker = workers.find(w=> !w.busy);

if(availableWorker) {
availableWorker.busy = true;
availableWorker.postMessage(iterations);
availableWorker.once("message", resolve);
}else {
queue.push({ iterations, resolve});
}
});
}

console.time("worker-pool");

Promise.all([
runJob(5e8),
runJob(5e8),
runJob(5e8),
runJob(5e8),
runJob(5e8),
]).then(() => {
console.timeEnd("worker-pool");
});
