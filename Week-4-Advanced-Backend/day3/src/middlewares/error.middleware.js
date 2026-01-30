module.exports = (err, req, res, next) => {
  res.status(500).json({
    success: false,
    message: err.message || "Internal Server Error",
    code: "INTERNAL_ERROR",
    timestamp: new Date().toISOString(),
    path: req.originalUrl
  });
};
