const express = require("express");
const loadExpress = require("./express");
const connectDB = require("./db");
const logger = require("../utils/logger");

module.exports = async function loadApp() {
  const app = express();

  logger.info("Loading middlewares...");
  loadExpress({ app });

  logger.info("Connecting database...");
  await connectDB();

  logger.info("Routes mounted: 0 endpoints (Day-1)");

  return app;
};
