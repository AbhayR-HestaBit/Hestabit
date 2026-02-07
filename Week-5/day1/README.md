# Day 1 - Docker Fundamentals And Linux Internals

## Folder Structure

```text 
├── day1/
│ ├── Dockerfile
│ ├── index.js
│ ├── package.json
│ ├── linux-in-container.md
│ ├── README.md
│ ├── linux-in-container.md
│ └── .gitignore
```

## Tasks done

- Built Node.js Docker image
- Ran container with port mapping
- Entered container using docker exec
- Explored Linux filesystem and processes


## How to Run
```bash
docker build -t day1 .
docker run -d -p 3000:3000 --name day1 day1
```

- For Seeing all running containers
```bash
docker ps
```

- For Viewing Logs in realtime 
```bash
docker logs -f day1
```

- For entering in running container
```bash
docker exec -it day1 sh
```

- For Stopping Container
```bash
docker stop day1
```

![Docker Build](screenshots/build-1.png)

![Commands Inside](screenshots/commad-1.png)

![Commands-2](screenshots/command-2.png)
