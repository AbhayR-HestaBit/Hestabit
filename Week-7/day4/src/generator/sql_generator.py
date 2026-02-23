import re
import logging
from pathlib import Path
from typing import Any, Optional
from src.generator.llm_client import LocalLLMClient
from src.utils.schema_loader import SchemaLoader

# Configure logging
logger = logging.getLogger(__name__)

class SQLGenerator:
    """
    Handles generating SQLite SQL queries from natural language questions using an LLM.
    """
    def __init__(self, llm_client: Any, schema_loader: SchemaLoader, prompt_path: str = 'src/prompts/sql_prompt.txt'):
        self.llm = llm_client
        self.loader = schema_loader
        self.prompt_path = Path(prompt_path)
        logger.info(f"SQLGenerator initialized with prompt path: {self.prompt_path}")

    def generate(self, question: str) -> str:
        """Generates a SQL query for a given question based on the loaded schema."""
        try:
            schema = self.loader.format_schema_for_prompt()
            if self.prompt_path.exists():
                template = self.prompt_path.read_text(encoding="utf-8")
                logger.debug(f"Loaded prompt template from {self.prompt_path}")
            else:
                template = "Schema:\n{schema}\nQuestion: {question}\nSQL:"
                logger.warning(f"Prompt template {self.prompt_path} not found, using default fallback.")
                
            prompt = template.format(schema=schema, question=question)
            raw_sql = self.llm.generate(prompt)
            
            cleaned_sql = self.clean_sql(raw_sql)
            logger.info(f"Generated SQL for question: '{question[:50]}...' -> {cleaned_sql[:100]}")
            return cleaned_sql
        except Exception as e:
            logger.error(f"Error during SQL generation: {e}")
            return ""

    def clean_sql(self, sql: str) -> str:
        """Cleans the raw LLM output to extract pure SQL."""
        if not sql:
            return ""
        # remove markdown blocks
        sql = re.sub(r'```sql\s*|\s*```', '', sql).strip()
        # remove mistral/inst tokens if they appear
        sql = sql.replace('[/INST]', '').strip()
        # remove trailing semicolon if any
        sql = sql.rstrip(';')
        return sql

    def fix_sql(self, question: str, bad_sql: str, error: str) -> str:
        """Attempts to fix a failing SQL query with the LLM by providing the error message."""
        try:
            logger.info(f"Attempting to fix SQL due to error: {error}")
            fix_prompt = f"""[INST] The SQL below failed: {bad_sql}
            Error: {error}
            Question: {question}
            Return ONLY the corrected SQLite SELECT SQL. [/INST]"""
            raw_sql = self.llm.generate(fix_prompt)
            return self.clean_sql(raw_sql)
        except Exception as e:
            logger.error(f"Failed to fix SQL: {e}")
            return bad_sql
