const helmet = require("helmet");
const cors = require("cors");
const rateLimit = require("express-rate-limit");

const generalLimiter = rateLimit({
  windowMs: 60 * 1000, 
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    return res.status(429).json({
      success: false,
      message: "Too many requests, please try again later",
    });
  },
});

const strictLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 2,
  handler: (req, res) => {
    return res.status(429).json({
      success: false,
      message: "Too many write requests",
    });
  },
});

const securityMiddlewares = [
  helmet(),
  cors({
    origin: ['http://localhost:5173'],
  }),
  generalLimiter,
];

module.exports = {
  securityMiddlewares,
  strictLimiter,
};
