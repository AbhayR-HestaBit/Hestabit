# SQL QA Doc

# Architecture
```text
Question
   |
LLM API and Schema Context
   |
Generated SQL Query
   |
SQL Validator
   |
SQLite (Read only)
   |
Raw Data Results
   |
LLM API
   |
Final Answer
```

## Steps
1. Extraction of Database schema.
2. Construction of a prompt for schema.
3. Validation of the generated SQL text for keywords.
4. Execution of the query on SQLite in read-only mode.
5. Formatting of the resulting data frame into text and summarization by AI.

## Read Only 
Used the SQLite URI mode to ensure the database cannot be modified:
`sqlite:///file:src/data/enterprise.db?mode=ro&uri=true`

## Prompt Design
Used the `[INST]` format. Prompt explicitly maintains to return **ONLY** the SQL to avoid parsing issues.

## Validation Rules
- **Safety:** Blocks keywords like `DROP`, `DELETE`, `UPDATE`.
- **Syntax:** Uses `sqlparse` to verify validity.
- **Single Statement:** Prevents SQL injection by blocking multi-statement queries.

## Sample Queries (customers table)
1. "How many customers subscribed in each year?"
2. "List the top 10 countries by number of customers."
3. "Show all customers whose last name is Smith."
4. "Which company has the most registered customers?"
5. "How many customers subscribed after 2021-01-01?"

## Code Snippet
**Schema Extraction:**
```python
def get_schema(self, table_name):
    with self.engine.connect() as conn:
        res = conn.execute(text(f"PRAGMA table_info({table_name})"))
        cols = [f"{r[1]} ({r[2]})" for r in res.fetchall()]
        return ", ".join(cols)
```

## Commands

```bash
source week7_env/bin/activate
# Build DB from CSV (run once)
python3 -m src.utils.create_sample_db
```
![DB Created](screenshots/db.png)

```bash
# NLP query
python3 -m src.pipelines.sql_pipeline --query "How many customers are from Denmark?"
```
![Query](screenshots/query.png)

```bash
# SQL query
python3 -m src.pipelines.run_pipeline --sql_query "Names of first 7 customers"
```
![SQL Query](screenshots/sql.png)