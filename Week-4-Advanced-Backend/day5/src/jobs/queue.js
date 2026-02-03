const { Queue } = require("bullmq");

const connection = {
  host: "127.0.0.1",
  port: 6379
};

const emailQueue = new Queue("email-queue", { connection });

module.exports = { emailQueue, connection };
