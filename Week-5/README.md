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
    
