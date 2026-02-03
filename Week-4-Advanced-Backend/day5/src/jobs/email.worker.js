const { Worker } = require("bullmq");
const { connection } = require("./queue");

const worker = new Worker(
  "email-queue",
  async job => {
    console.log("Email job processed:", job.data);
  },
  {
    connection,
    attempts: 3,
    backoff: {
      type: "exponential",
      delay: 2000
    }
  }
);

worker.on("failed", (job, err) => {
  console.error(`Job ${job.id} failed:`, err.message);
});
