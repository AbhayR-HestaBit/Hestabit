#!/usr/bin/env node
const fs=require("fs")
const path=require("path")
const{Worker}=require("worker_threads")

const args=process.argv.slice(2)

function parseArgs(args){
const options={file:null,top:10,minLen:1,unique:false,workers:1}
for(let i=0;i<args.length;i++){
const arg=args[i]
if(arg==="--file")options.file=args[++i]
else if(arg==="--top")options.top=Number(args[++i])
else if(arg==="--minLen")options.minLen=Number(args[++i])
else if(arg==="--unique")options.unique=true
else if(arg==="--workers")options.workers=Number(args[++i])
}
return options
}

const options=parseArgs(args)

if(!options.file){console.error("Error: --file is required");process.exit(1)}
if(!fs.existsSync(options.file)){console.error("Error: file does not exist");process.exit(1)}
if(options.workers<=0||isNaN(options.workers)){console.error("Error: --workers must be positive");process.exit(1)}

const workers=[]
const queue=[]

for(let i=0;i<options.workers;i++){
const worker=new Worker(path.resolve("src/word-worker.js"))
worker.busy=false
workers.push(worker)
}

function runJob(text){
return new Promise(resolve=>{
const available=workers.find(w=>!w.busy)
if(available){
available.busy=true
available.once("message",result=>{
available.busy=false
if(queue.length>0){
const next=queue.shift()
runJob(next.text).then(next.resolve)
}
resolve(result)
})
available.postMessage(text)
}else{
queue.push({text,resolve})
}
})
}

const counts=new Map()
let totalWords=0
let longestWord=""
let shortestWord=""

function merge(result){
totalWords+=result.total
for(const[word,count]of Object.entries(result.freq)){
if(word.length>=options.minLen){
counts.set(word,(counts.get(word)||0)+count)
}
}
if(!longestWord||result.longest.length>longestWord.length)longestWord=result.longest
if(!shortestWord||result.shortest.length<shortestWord.length)shortestWord=result.shortest
}

let leftover=""
let processing=Promise.resolve()

const stream=fs.createReadStream(options.file,{encoding:"utf8"})

stream.on("data",chunk=>{
stream.pause()
processing=processing.then(async()=>{
const text=leftover+chunk
const parts=text.split(/\s+/)
leftover=parts.pop()
const payload=parts.join(" ")
if(payload){
const result=await runJob(payload)
merge(result)
}
stream.resume()
})
})

stream.on("end",async()=>{
await processing
if(leftover){
const result=await runJob(leftover)
merge(result)
}
let results=[...counts.entries()]
if(options.unique)results=results.filter(([_,c])=>c===1)
results.sort((a,b)=>b[1]-a[1])
results=results.slice(0,options.top)
const output={
file:options.file,
workers:options.workers,
totalWords,
uniqueWords:counts.size,
longestWord,
shortestWord,
topWords:results
}
fs.mkdirSync("output",{recursive:true})
fs.writeFileSync("output/stats.json",JSON.stringify(output,null,2))
await Promise.all(workers.map(w=>w.terminate()))
})

