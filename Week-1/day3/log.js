//TODO: error detection logic
//temporary comment
//console.log("processing log file")
const fs=require("fs")
function parseLine(line){return line.trim()}
function isError(line){return line.includes("ERROR")}
function countErrors(lines){
let c=0
for(const l of lines)if(isError(l))c++
return c
}
const logs=fs.readFileSync("app.log","utf8").split("\n")
console.log("Total Error Count:",countErrors(logs))
