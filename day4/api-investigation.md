# Day-4 HTTP, Networking & Server Investigation

worked on understanding how http request actually works from client to server and what happens in between without using any framework.


## Directory Structure

```day4/
├── server.js
├── api-investigation.md
├──screenshots
├──curl-lab.txt```

## Network and DNS Investigation

Commands used:

```abhayrajput@hestabit-LP:~/Desktop/Tasks/day4$ nslookup dummyjson.com
Server:		127.0.0.53
Address:	127.0.0.53#53

Non-authoritative answer:
Name:	dummyjson.com
Address: 172.67.205.42
Name:	dummyjson.com
Address: 104.21.61.23
Name:	dummyjson.com
Address: 2606:4700:3033::6815:3d17
Name:	dummyjson.com
Address: 2606:4700:3031::ac43:cd2a
```

to see how request travels hop by hop from my system to the server.

observed that before any http request dns resolution happens first and packets pass through multiple routers.

---

## Working with curl

used curl to inspect http requests and responses.

Commands:
```abhayrajput@hestabit-LP:~/Desktop/Tasks/day4$ traceroute dummyjson.com
```


to see how request travels hop by hop from my system to the server.

observed that before any http request dns resolution happens first and packets pass through multiple routers.

---

## Working with curl

used curl to inspect http requests and responses.

Commands:

```abhayrajput@hestabit-LP:~/Desktop/Tasks/day4$ curl -v dummyjson.com```


to inspect request headers, response headers, status code and server metadata.


```abhayrajput@hestabit-LP:~/Desktop/Tasks/day4$ curl -i dummyjson.com```


to check headers along with response body.

```curl -H "X-Test: hello" http://localhost:3000/echo```

to send custom headers and verify what server receives.

```abhayrajput@hestabit-LP:~/Desktop/Tasks/day3$ curl -H "X-Test: hello" http://localhost:3000/echo
hello
```

to send custom headers and verify what server receives.

```
abhayrajput@hestabit-LP:~/Desktop/Tasks/day3$ curl -i http://localhost:3000/cache
curl -i -H 'If-None-Match: v1-static' http://localhost:3000/cache
HTTP/1.1 200 OK
Cache-Control: public, max-age=60
ETag: v1-static
Date: Mon, 12 Jan 2026 12:51:49 GMT
Connection: keep-alive
Keep-Alive: timeout=5
Content-Length: 16

cached response
HTTP/1.1 304 Not Modified
Cache-Control: public, max-age=60
ETag: v1-static
Date: Mon, 12 Jan 2026 12:51:49 GMT
Connection: keep-alive
Keep-Alive: timeout=5
```

to inspect cache headers like cache-control and etag.

```abhayrajput@hestabit-LP:~/Desktop/Tasks/day3$ curl -i -H "if-None-Match:v1-static" http://localhost:3000/cache
HTTP/1.1 304 Not Modified
Cache-Control: public, max-age=60
ETag: v1-static
Date: Mon, 12 Jan 2026 13:33:04 GMT
Connection: keep-alive
Keep-Alive: timeout=5
```


which returned 304 not modified showing conditional caching works.

---

## Working with Postman

verified same endpoints using postman for better visualization.

Endpoints tested:

```GET /
GET /health
GET /slow?ms=3000
GET /echo
GET /cache```


actions done in postman:
- added custom headers
- inspected request and response headers
- tested delayed response
- tested conditional request using if-none-match

---

## Node.js HTTP Server Implementation

created a minimal http server using node.js http module without using any framework.

file used: `server.js`

endpoints implemented:

```/ -> basic response to verify server is running
/health -> returns simple ok response used as health check
/slow -> simulates slow request using settimeout
/echo -> returns request method, url and headers
/cache -> implements http caching using etag and cache-control```


---

## Observations

- http is stateless and header driven
- health endpoint should be lightweight
- slow requests should not block other requests
- caching is controlled by headers not server logic
- curl gives raw view, postman gives visual view


