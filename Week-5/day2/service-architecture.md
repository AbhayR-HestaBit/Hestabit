# System Architecture - Day 2 (Docker Compose)

A multi-container application managed using Docker Compose.

## Services

### Client (React/HTML)
- Runs as a separate container
- Exposes port `3000` to the host
- Sends HTTP requests to the backend service

### Server (Node.js API)
- Runs as a separate container
- Exposes port `5000` to the host
- Handles API requests and connects to MongoDB

### MongoDB
- Runs as a database container
- Does not expose any port to the host
- Stores data in a Docker volume for persistence

## Working

```text
Browser
   |
   v
Client Container (3000)
   |
   v
Server Container (5000)
   |
   v
MongoDB Container (27017)
```
## Commands 

- For starting all containers
```bash
docker compose up -d
```

- For stopping containers
```bash
docker compose stop
```

- For restarting stopped containers 
```bash
docker compose start
```

- For Stopping and removing containers
```bash
docker compose down
```

- For Stopping and removing containers with persistent data
```bash
docker compose down -v
```

- For seeing running containers
```bash
docker compose ps
```

- For seeing logs of all services
```bash
docker compose logs
```

- For continuously streaming logs
```bash
docker compose logs -f
``` 
