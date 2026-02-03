# Day 3 - Database Modeling, Indexing and Advanced CRUD  

## Folder Structure

```text 
day3
└── src
│    ├── config
│    ├── controllers
│    │   └── product.controller.js
│    ├── jobs
│    ├── loaders
│    │   ├── app.js
│    │   └── db.js
│    ├── middlewares
│    │   └── error-middleware.js
│    ├── models
│    │   ├── Product.js
│    │   └── User.js
│    ├── repositories
│    │   ├── product.repository.js
│    │   └── user.repository.js
│    ├── routes
│    ├── services
│    │   └── product.service.js
│    └── utils
│        └── logger.js
└── QUERY-ENGINE-DOC.md
└── README.md

```

## Tasks done

- Created User and Product database schemas
- Added data validation and constraints
- Implemented password hashing using pre-save hook
- Built repository layer to abstract database operations
- Verified implementation using MongoDB and Node execution

## Models

### User Model (`src/models/User.js`)

- Define user data structure
- Enforce unique email constraint
- Secure password storage

### Product Model (`src/models/Product.js`)

- Define product structure
- Enable efficient product listing and filtering
- Prepare data for future APIs

