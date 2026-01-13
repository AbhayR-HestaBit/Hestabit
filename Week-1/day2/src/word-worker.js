const{parentPort}=require("worker_threads")

parentPort.on("message",text=>{
const freq={}
let total=0
let longest=""
let shortest=""
const words=text.toLowerCase().replace(/[^a-z0-9\s]/g,"").split(/\s+/).filter(Boolean)
for(const word of words){
total++
freq[word]=(freq[word]||0)+1
if(!longest||word.length>longest.length)longest=word
if(!shortest||word.length<shortest.length)shortest=word
}
parentPort.postMessage({total,freq,longest,shortest})
})

