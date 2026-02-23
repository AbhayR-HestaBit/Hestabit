import re
from pathlib import Path
from src.generator.llm_client import LocalLLMClient
from src.utils.schema_loader import SchemaLoader

class SQLGenerator:
    def __init__(self, llm_client, schema_loader):
        self.llm = llm_client
        self.loader = schema_loader
        self.prompt_path = Path('src/prompts/sql_prompt.txt')

    def generate(self, question):
        schema = self.loader.format_schema_for_prompt()
        if self.prompt_path.exists():
            template = self.prompt_path.read_text()
        else:
            template = "Schema:\n{schema}\nQuestion: {question}\nSQL:"
            
        prompt = template.format(schema=schema, question=question)
        raw_sql = self.llm.generate(prompt)
        
        return self.clean_sql(raw_sql)

    def clean_sql(self, sql):
        # remove markdown blocks
        sql = re.sub(r'```sql\s*|\s*```', '', sql).strip()
        # remove mistral/inst tokens if they appear
        sql = sql.replace('[/INST]', '').strip()
        # remove trailing semicolon if any
        sql = sql.rstrip(';')
        return sql

    def fix_sql(self, question, bad_sql, error):
        fix_prompt = f"""[INST] The SQL below failed: {bad_sql}
        Error: {error}
        Question: {question}
        Return ONLY the corrected SQLite SELECT SQL. [/INST]"""
        raw_sql = self.llm.generate(fix_prompt)
        return self.clean_sql(raw_sql)
