# Day 2 — Database Modeling, Indexing and Advanced CRUD  

## Folder Structure

```text 
day2
└── src
│    ├── config
│    ├── controllers
│    ├── jobs
│    ├── loaders
│    │   ├── app.js
│    │   └── db.js
│    ├── middlewares
│    ├── models
│    │   ├── Product.js
│    │   └── User.js
│    ├── repositories
│    │   ├── product.repository.js
│    │   └── user.repository.js
│    ├── routes
│    ├── services
│    └── utils
│        └── logger.js
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

