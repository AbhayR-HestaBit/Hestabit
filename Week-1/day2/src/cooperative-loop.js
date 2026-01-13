let count= 0;

function heavyWorkChunk() {
const start = Date.now();

while (Date.now() - start <50) {
count++;
}
if (count < 1e7){
setImmediate(heavyWorkChunk);
}else{
console.log("work complete:", count);
}
}

console.log("Starting cooperative work");

setTimeout(() => {
console.log("Timer executed during work");
}, 0);

heavyWorkChunk();
