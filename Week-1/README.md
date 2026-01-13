# Week 1 

## Folder Structure

Below is the required Directory Structure to navigate:

week1/
├── day1/
│ ├── README.md
│ ├── system-report.md
│ ├── introspect.js
│ └── logs/
│
├── day2/
│ ├── README.md
│ ├── wordstat.js
│ ├── corpus.txt
│ ├── output/
│ └── logs/
│
├── day3/
│ ├── log.js
│ ├── app.log
│ └── README.md
│
├── day4/
│ ├── server.js
│ ├── curl-lab.txt
│ ├── api-investigation.md
│ └── README.md
│
├── day5/
│ ├── app.js
│ ├── validate.sh
│ ├── config.json
│ ├── artifacts/
│ ├── .husky/
│ └── README.md
│
└── WEEK1-RETRO.md

---

### Day 1 — System & Runtime Understanding
- Linux filesystem, permissions, shell usage
- Node.js runtime inspection
- NVM and Node version management
- Stream vs buffer memory behavior
- Measuring execution time and memory usage

### Day 2 — CLI Engineering & Concurrency
- Built a production-style CLI tool (`wordstat.js`)
- Processed large files using streams
- Implemented worker threads and worker pool
- Applied backpressure and queueing
- Benchmarked performance across worker counts

### Day 3 — Git Recovery & Debugging
- Multi-commit workflow
- Introduced controlled bugs
- Used git bisect to locate faulty commit
- Reverted bugs safely
- Used stash and merge conflict resolution


### Day 4 — HTTP & Networking Fundamentals
- Understood HTTP request lifecycle
- Used curl, nslookup, traceroute
- Built a raw Node.js HTTP server without frameworks
- Implemented routing, health endpoint, and defensive responses
- Analyzed headers, status codes, caching, keep-alive


### Day 5 — Automation & Mini CI Pipeline
- Built validation scripts
- Enforced linting and formatting
- Implemented pre-commit hooks using Husky
- Prevented bad commits automatically
- Generated build artifacts with checksums
- Scheduled tasks using cron

Artifacts:
- validate.sh
- ESLint + Prettier config
- Husky hooks
- build artifacts (.tgz + sha256)
- cron execution logs

---

## How to Navigate

- Follow execution logs and scripts
- Check git history for learning progression
- Can Refer `WEEK1-RETRO.md` for lessons learned
