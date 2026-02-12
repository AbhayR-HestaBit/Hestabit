# Day 4 - SSL, Self-Signed, mkcert And HTTPS

## Folder Structure

```text
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
```

## Tasks Done

- Generated browser-trusted certificates using mkcert
- Configured NGINX for HTTPS
- Mounted SSL certificates into NGINX container
- Verified secure access using curl and browser
- Ran services using Docker Compose

## Commands Used

- For generating certificates

```bash
mkcert localhost 127.0.0.1
```

![Generate Certificate](screenshots/mkcert.png)

- For building container
```bash
docker compose up -d
```

![Compose](screenshots/compose.png)

- For seeing logs
```bash
docker compose logs
```

![Logs](screenshots/logs.png)

## Verification and testing

- Over CLI

```bash
curl https://localhost/api
```

![Certificate-CLI](screenshots/cert-cli.png)

- Inside Browser

![Certificate](screenshots/cert-1.png)


