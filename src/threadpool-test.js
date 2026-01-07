const crypto = require("crypto");

const start = Date.now();

function runTask(i) {
crypto.pbkdf2("password", "salt" , 100000, 64, "sha512", () => {
console.log(`Task ${i} done at ${Date.now() - start}ms`);
});
}

for (let i = 1; i <= 10; i++) {
runTask(i);
}
