

## Step 1: Install Dependencies

```bash
npm install
```

## Step 2: Set Up Environment Files

I created three environment files as required:

- `.env.local` - for local development
- `.env.dev` - for development server
- `.env.prod` - for production

**.env.prod:**

```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/week4_local

```

## Step 3: Start MongoDB

```bash
sudo systemctl start mongod
sudo systemctl status mongod

mongo
```

## Step 4: Start Redis (for Job Queues)

```bash
# Install Redis (if not installed)
sudo apt-get install redis-server

# Start Redis
redis-server

# Check if Redis is working
redis-cli ping
```

## Database Setup 

## Creating Indexes

Created indexes in User and Product models:

**In /models/User.js:**
- Email index (unique)
- Compound index: `{ status: 1, createdAt: -1 }`

**In /models/Product.js:**
- Compound index: `{ status: 1, createdAt: -1 }`

## Running the Application

### With Node Command

```bash
node src/index.js
```

or if you set up scripts in package.json:

```bash
npm start
```

### With PM2

PM2 keeps the app running even after server restart.

**Install PM2:**
```bash
npm install -g pm2
```

**ecosystem.config.js file (in /prod folder):**

```javascript
module.exports = {
  apps: [
    {
     name: "backend-week4-api",
      script: "src/server.js",

      env_production: {
        NODE_ENV: "prod",
        PORT: 3000
      },

      instances: "max",
      exec_mode: "cluster",

      autorestart: true,
      watch: false,
      max_memory_restart: "500M",

      error_file: "src/logs/pm2-error.log",
      out_file: "src/logs/pm2-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss"
    }
  ]
};
```

**Start with PM2:**
```bash
pm2 start prod/ecosystem.config.js --env production
```

**Useful PM2 Commands:**
```bash
# Check if app is running
pm2 list

# View logs
pm2 logs
```

## Background Jobs

`/jobs/email.job.js` uses BullMQ for background processing.

**Start the worker process:**
```bash
node src/jobs/email.job.js
```

Or add it to PM2 ecosystem.config.js as a separate process.

---

## Logging 

I used Winston for logging in `/utils/logger.js`.

**Log files are in `/logs` folder:**
- app.log
- error.log


**Startup logs show:**
```
✔ Server started on port 3000
✔ Database connected
✔ Middlewares loaded
✔ Routes mounted: 23 endpoints
```


## Security Features 

 `/middlewares/security.js`:

**1. Helmet** - Sets security HTTP headers
```bash
npm install helmet
```

**2. CORS** - Controls which domains can access the API
```bash
npm install cors
```

**3. Rate Limiting** - Prevents too many requests from same IP
```bash
npm install express-rate-limit
```

**4. Input Validation** - Uses JOI/Zod in `/middlewares/validate.js`
```bash
npm install joi
```

## Testing the API

**Test if server is running:**
```bash
curl http://localhost:3000
```

**Test with Postman:**
- Import Postman Collection (exported in Week 4 Day 5)
- Set environment variables in Postman {BaseURL and productId}
- Test all endpoints

**Example Product API endpoint:**
```
GET /products?search=phone&minPrice=100&maxPrice=500&sort=price:desc
```


## Issues occured

### Issue 1: Port Already in Use
**Error:** `EADDRINUSE: address already in use :::3000`

**Solution:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill that process
kill -9 
```

### Issue 2: MongoDB Connection Failed
**Error:** `MongoServerError: Authentication failed`

**Solution:**
- Check MONGODB_URI in .env file
- Make sure MongoDB service is running: `sudo systemctl status mongod`
- Test connection manually: `mongo`

### Issue 3: Redis Not Connected
**Error:** `Error: connect ECONNREFUSED`

**Solution:**
```bash
# Start Redis
redis-server

# Or as a service
sudo systemctl start redis
```

### Issue 4: Module Not Found
**Error:** `Cannot find module 'express'`

**Solution:**
```bash
# Reinstall dependencies
npm install
```

---
