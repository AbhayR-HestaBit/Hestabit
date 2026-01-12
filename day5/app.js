function getTimestamp() {
  return new Date().toISOString();
}

function logStartup() {
  const message = `Application started at ${getTimestamp()}`;
  console.log(message);
  return message;
}

if (require.main === module) {
  logStartup();
}

module.exports = {
  logStartup,
};
// break
