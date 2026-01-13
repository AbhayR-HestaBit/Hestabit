# Day -1 System Reverse Engineering With Node & Terminal Mastering

## System Identification

Using terminal commands, the following system details were identified and documented:

- OS Version
- Current shell
- Node binary path
- NPM global installation path
- PATH entries related to node and npm

All findings were documented inside `system-report.md` along with screenshots.

## NVM Installation and Node Version Switching

Installed Node Version Manager (NVM) to control Node runtime versions.


## System Introspection Script

Created `introspect.js` which prints runtime and system level information.

The script outputs:

- OS
- Architecture
- CPU cores
- Total memory
- System uptime
- Current logged-in user
- Node binary path

Executed using:

node introspect.js

## Stream vs Buffer Performance Test

Generated a large file greater than 50MB using terminal.

Command:

dd if=/dev/urandom of=bigfile.txt bs=1M count=50

The file was read using two approaches:

1. Buffer-based reading using fs.readFile
2. Stream-based reading using fs.createReadStream

Execution time and memory usage were measured using:

console.time 
process.memoryUsage()

Results were stored inside:

logs/day1-perf.json

## Deliverables

- system-report.md
- introspect.js
- logs/day1-perf.json
- Performed 6+ meaningful commits (verified using git log)

