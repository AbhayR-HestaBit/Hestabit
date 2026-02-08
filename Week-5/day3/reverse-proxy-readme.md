# Reverse Proxy & Load Balancing

Browser requests are sent to NGINX, which forwards them to backend
containers running the same Node.js application.

## Working Flow:

```text
(Browser / curl)
        |
        |  http://localhost:8080/api
        |
        v
NGINX (Reverse Proxy)
   - Runs inside Docker
   - Listens on port 80
   - Entry point for all requests
        |
        |  (Docker internal network)
        |
        ----------------------
        |                    |
        v                    v
Backend #1               Backend #2
 (Node.js)               (Node.js)
 Port: 3000              Port: 3000
 hostname:20b80a1eec53    hostname: 757abc447126
```

## Load Balancing

- Backend service is scaled to multiple instances
- Docker DNS resolves the service name to multiple container IPs
- NGINX distributes requests using round-robin strategy by default

## Commands Used

- For building container
```bash
docker compose up -d
```

![Compose](screenshots/compose-1.png)

- For building container
```bash
docker logs day3-nginx-1
```

![Logs](screenshots/logs.png)
