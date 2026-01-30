const mongoose = require("mongoose");
const config = require("../config");
const logger = require("../utils/logger");

module.exports = async function connectDB() {
  try {
    await mongoose.connect(config.mongoUri);
    logger.info("Database connected");
  } catch (error) {
    logger.error("Database connection failed");
    logger.error(error.message);
    process.exit(1);
  }
};
