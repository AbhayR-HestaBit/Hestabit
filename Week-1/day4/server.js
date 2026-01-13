const http=require("http")
const url=require("url")

const RATE_LIMIT=5
const WINDOW_MS=10000
const MAX_CONCURRENT=2
let active=0
const queue=[]

const clients=new Map()

function isRateLimited(ip){
const now=Date.now()
let entry=clients.get(ip)

if(!entry){
clients.set(ip,{count:1,start:now})
return false
}

if(now-entry.start>WINDOW_MS){
clients.set(ip,{count:1,start:now})
return false
}

entry.count++
return entry.count>RATE_LIMIT
}

const server=http.createServer((req,res)=>{
const ip=req.socket.remoteAddress
const parsed=url.parse(req.url,true)

if(isRateLimited(ip)){
res.statusCode=429
res.end("Too Many Requests\n")
return
}

if(parsed.pathname==="/slow"){
const ms=Number(parsed.query.ms)||2000

const job=()=>{
active++
setTimeout(()=>{
res.statusCode=200
res.end("done\n")
active--
if(queue.length>0){
const next=queue.shift()
next()
}
},ms)
}

if(parsed.pathname==="/echo"){
res.statusCode=200
res.setHeader("Content-Type","application/json")
res.end(JSON.stringify({
method:req.method,
url:req.url,
headers:req.headers
},null,2))
return
}

if(active<MAX_CONCURRENT){
job()
}else{
queue.push(job)
}
return
}

if(parsed.pathname==="/health"){
res.statusCode=200
res.end("ok\n")
return
}

if(parsed.pathname==="/cache"){
const etag="v1-static"
res.setHeader("Cache-Control","public, max-age=60")
res.setHeader("ETag",etag)

if(req.headers["if-none-match"]===etag){
res.statusCode=304
res.end()
return
}

res.statusCode=200
res.end("cached response\n")
return
}


res.statusCode=200
res.end("hello\n")
})

server.listen(3000,()=>console.log("listening on 3000"))
