console.log("Start");

setTimeout(() => {
console.log("Timeout executed at", Date.now());
}, 0);
console.log("Start at", Date.now());

//cpu bound block 
const start = Date.now();
while (Date.now() - start <3000){
//busy
}

console.log("End of cpu task");
