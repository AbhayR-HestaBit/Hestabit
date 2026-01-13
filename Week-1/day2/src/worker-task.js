const { parentPort } = require("worker_threads");

parentPort.on("message", (iterations) => {
let count = 0;
for (let i=0; i< iterations; i++) {
count +=i;
}
parentPort.postMessage(count);
});
