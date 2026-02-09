# Week 5 - Server Side Foundations

## Folder Structure

```text
Week-5/
├── day1/
│ ├── Dockerfile
│ ├── index.js
│ ├── package.json
│ ├── linux-in-container.md
│ ├── README.md
│ ├── linux-in-container.md
│ └── .gitignore
│ └── README.md
├── day2/
│ ├── docker-compose.yml
│ ├── system-architecture.md
│ ├── README.md
│ ├── .gitignore
│ ├── server/
│ │ ├── Dockerfile
│ │ ├── index.js
│ │ └── package.json
│ └── client/
│ │ ├── Dockerfile
│ │ ├── package.json
│ │ ├── public/
│ │ └── src/
├──day3/
│ ├── docker-compose.yml
│ ├── reverse-proxy-readme.md
│ ├── README.md
│ ├── nginx/
│ │ └── nginx.conf
│ └── backend/
│ ├── Dockerfile
│ ├── index.js
│ └── package.json
day4/
│ ├── docker-compose.yml
│ ├── ssl-setup.md
│ ├── README.md
│ ├── nginx/
│ │ ├── nginx.conf
│ └── certs/
│ │ ├── server.crt
│ │ └── server.key
│ └── backend/
│ │ ├── Dockerfile
│ │ ├── index.js
│ │ └── package.json
day5/
│
├── backend/
│   ├── Dockerfile
│   ├── index.js
│   ├── package.json
│   └── .dockerignore
│
├── client/
│   ├── Dockerfile
│   ├── index.html
│   └── .dockerignore
│
├── nginx/
│   ├── nginx.conf
│   └── certs/
│       ├── server.crt
│       └── server.key
│
├── docker-compose.yml
└── README.md

```

### Day 1 - Docker Fundamentals & Linux Internals

- Installed Docker Engine and Docker Compose
- Built a Docker image using Dockerfile
- Ran and exposed container over HTTP
- Entered container and explored Linux internals
- Inspected processes, filesystem, logs


### Day 2 - Docker Compose & Multi-Container Application

- Created a multi-container application using Docker Compose
- Built a server and client service
- Added MongoDB as a database container
- Managed all services using a single `docker compose up -d` command

### Day 3 - NGINX Reverse Proxy And Load Balancing

- Configured NGINX as a reverse proxy
- Scaled backend service to multiple instances
- Implemented round-robin load balancing
- Verified load balancing using container hostnames

### Day 4 - SSL, Self-Signed, mkcert And HTTPS

- Generated browser-trusted certificates using mkcert
- Configured NGINX for HTTPS
- Mounted SSL certificates into NGINX container
- Verified secure access using curl and browser
- Ran services using Docker Compose

### Day 5 - CI-Style Deployment Automation & Capstone

- Multi Container Docker setup
- Reverse Proxy Configuration
- Https Setup
- Health check config
