# Day -2 Node CLI App With  Concurrency And Large Data Processing

## Corpus Generation

A large corpus text file was generated containing more than 200,000 words.

Method used:
- Scripted generation of words (word1 to word250000)

File created:
corpus.txt

## CLI Tool: wordstat.js

Built an executable Node CLI tool which accepts arguments via command line.

Command:

```node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique --workers 4```

Arguments used:

--file     Input file pat
--top      Top N repeated words
--minLen   Minimum word length 
--unique   Show words appearing only once
--workers  Number of worker threads

## Output Metrics

The CLI computes and outputs:

- Total number of words
- Number of unique words
- Longest word
- Shortest word
- Top N most frequent words

Final results were stored in:

output/stats.json

## Concurrency Implementation

The file was processed using:

- Chunk-based reading
- worker_threads for parallel processing
- Internal worker pool with queueing
- Backpressure handling using stream.pause() and stream.resume()

Concurrency levels tested:

- 1 worker
- 4 workers
- 8 workers

## Performance Benchmarking

Execution time was measured for each concurrency level.

Logs captured in:

logs/perf-summary.json

This allowed comparison of:
- Single-threaded vs parallel processing
- CPU utilization
- Throughput improvement

## Error Handling & Validation

Implemented validation for:

- Missing file
- Invalid CLI arguments
- Worker failures

## Commits

Peromed around 8 commits were made documenting:
- Argument parsing
- Word counting logic
- Worker thread integration
- Performance optimization
- Bug fixes

Verified using:

git log --oneline

## Deliverables

- wordstat.js
- corpus.txt
- output/stats.json
- logs/perf-summary.json
- Minimum 8 commits
