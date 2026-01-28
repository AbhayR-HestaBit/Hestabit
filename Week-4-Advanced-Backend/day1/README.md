# Day 1 — Node.js, Project Architecture 

## Folder Structure

```text 
Day-1
 └──src/
 │   ├── config/
 │   │
 │   ├── loaders/
 │   │   ├── app.js
 │   │   └── db.js
 │   ├── utils/
 │   │   └── logger.js
 │   │
 │   ├── models/
 │   ├── routes/
 │   ├── controllers/
 │   ├── services/
 │   ├── repositories/
 │   ├── middlewares/
 │   ├── jobs/
 │   ├── logs/
 └── README.md
```

## Tasks done

- Environment config
- Express middleware setup
- MongoDB connection with failure handling
- Centralized logging using Winston
- Controlled startup using loaders
- Architecture documentation

## What Each Layer Does

### server.js
Entry point of the application.
Responsible only for bootstrapping the app and starting the server.

### config/
Handles environment configuration.
- Loads `.env.local`, `.env.dev`, or `.env.prod`
- Prevents direct usage of `process.env` across the app

### loaders/
Controls application startup order.
- db loader → database connection
- app loader → orchestrates startup sequence

### utils/
Reusable utilities used across the project.
- Winston logger for structured logging

### logs/
Stores application logs.
- app.log → general logs
- error.log → error-level logs

