# Production Guide – Day 5 Deployment

## Flow of Request

```text
+-------------------+
|      Browser      |
|  (User Interface) |
+-------------------+
          |
          v
        (HTTPS)
+-------------------+
|       Nginx       |
|  Reverse Proxy    |
|                   |
+-------------------+
      |           |
      |           |
      v           v
+-----------+   +----------------+
|  Client   |   |    Backend     |
|  React    |   |  Node + Express|
|           |   |                |
+-----------+   +----------------+
                          |
                          v
                  +----------------+
                  |    MongoDB     |
                  |                |
                  +----------------+
```

## Container and their Working

### Backend

- Handles REST API
- Connects to MongoDB
- Logs requests
- Exposes /health

### Client

- React production build
- Served through Nginx

### MongoDB

- Persistent data storage
- Docker volume mounted

### Nginx

- SSL termination
![Secured](screenshots/cert.png)
- Reverse proxy routing
- Serves frontend
- Proxies /api to backend

## Project Structure 

```text 
day5/
│
├── backend/
│ ├── Dockerfile
│ ├── package.json
│ └── index.js
│
├── client/
│ ├── Dockerfile
│ ├── package.json
│ └── src/
│
├── nginx/
│ ├── nginx.conf
│ └── certs/
│
├── docker-compose.yml
├── .env
├── README.md
└── production-guide.md
```

## Check for Routes:

- For Client <a href="https://localhost">https://localhost</a>
- For Backend Health <a href="https://localhost/health">https://localhost/health</a>
- For Api Notes <a href="https://localhost/api/notes">https://localhost/api/notes</a>

### Commands:

- For building and starting containers `docker compose up -d --build`
![Compose](screenshots/compose.png)
- For Stopping containers `docker compose down`
- For viewing running containers `docker ps`
![Running Contianers](screenshots/running.png)

### Troubleshooting:

- Check logs `docker logs <container-name>`
- Can be done over all the running containers to check where is the problem residing


