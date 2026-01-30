const { createLogger, format, transports } = require("winston");

const logger = createLogger({
  level: "info",
  format: format.combine(
    format.timestamp(),
    format.printf(({ level, message, timestamp }) => {
      return `[${timestamp}] ${level.toUpperCase()}: ${message}`;
    })
  ),
  transports: [
    new transports.File({
      filename: "src/logs/error.log",
      level: "error"
    }),
    new transports.File({
      filename: "src/logs/app.log"
    })
  ]
});

if (process.env.NODE_ENV !== "prod") {
  logger.add(new transports.Console());
}

module.exports = logger;
