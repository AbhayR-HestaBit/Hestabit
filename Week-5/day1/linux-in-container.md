# Linux Inside a Docker Container

## How Port is working inside docker

```text
Browser
  |
  v
Host Machine (localhost:3000)
  |
  |  -p 3000:3000
  v
Docker Engine
  |
  v
Container (port 3000)
  |
  v
Node.js Application
```


