# Day 5 - JOB QUEUES, LOGGING, API DOCUMENTATION AND CAPSTONE 

## Folder Structure

```text 
day5
├── DEPLOYMENT-NOTES.md
├── postman_collection_week_4.json
└── src
    ├── config
    ├── controllers
    │   └── product.controller.js
    ├── jobs
    │   ├── email.job.js
    │   ├── email.worker.js
    │   └── queue.js
    ├── loaders
    │   ├── app.js
    │   └── db.js
    ├── logs/
    ├── middlewares
    │   ├── error.middleware.js
    │   ├── security.js
    │   └── validate.js
    ├── models
    │   ├── Product.js
    │   └── User.js
    ├── repositories
    │   ├── product.repository.js
    │   └── user.repository.js
    ├── routes
    ├── services
    │   └── product.service.js
    └── utils
        ├── logger.js
        └── tracing.js
─ README.md


```

## Tasks done

- Background job integration using BullMQ
- Worker process setup and logging
- Logs correlated with request ID
- API documentation via Postman Collection
- Production-ready setup using PM2
- Ecosystem configuration for deployment


