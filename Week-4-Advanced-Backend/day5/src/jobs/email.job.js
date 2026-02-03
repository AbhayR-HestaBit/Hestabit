const queue = [];

function addEmailJob(data) {
  queue.push(data);
  processQueue();
}

function processQueue() {
  while (queue.length) {
    const job = queue.shift();
    console.log("📧 Email job processed:", job);
  }
}

module.exports = { addEmailJob };
