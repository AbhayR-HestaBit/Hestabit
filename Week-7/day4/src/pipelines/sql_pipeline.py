from sqlalchemy import create_engine, text
import pandas as pd
from src.generator.llm_client import LocalLLMClient
from src.utils.schema_loader import SchemaLoader
from src.generator.sql_generator import SQLGenerator
from src.utils.sql_validator import SQLValidator

class SQLQAPipeline:
    # orchestrates generating, validating, and running an sql query against the sqlite db
    def __init__(self, db_path='src/data/enterprise.db'):
        self.db_path = db_path
        self.loader = SchemaLoader(db_path)
        self.llm = LocalLLMClient()
        self.generator = SQLGenerator(self.llm, self.loader)
        self.validator = SQLValidator(known_tables=self.loader.get_table_names())
        
        # Read-only engine
        self.engine = create_engine(
            f'sqlite:///file:{db_path}?mode=ro&uri=true',
            connect_args={'check_same_thread': False}
        )

    def run(self, question, max_retries=2):
        # runs the entire pipeline: generates sql, verifies safety, executes, and creates a text summary
        retries = 0
        sql = self.generator.generate(question)
        
        while retries <= max_retries:
            val_res = self.validator.validate(sql)
            if val_res['valid']:
                try:
                    with self.engine.connect() as conn:
                        res = conn.execute(text(sql))
                        df = pd.DataFrame(res.fetchall(), columns=res.keys())
                    
                    # summarize
                    summary_prompt = f"""[INST] Question: {question}
                    SQL Result:
                    {df.to_string(max_rows=20)}
                    Summarize the findings in 2-3 natural sentences. [/INST]"""
                    summary = self.llm.generate(summary_prompt)
                    
                    return {
                        'question': question,
                        'sql': sql,
                        'result': df,
                        'summary': summary,
                        'retries': retries,
                        'error': None
                    }
                except Exception as e:
                    error_str = str(e)
                    if retries < max_retries:
                        sql = self.generator.fix_sql(question, sql, error_str)
                        retries += 1
                        continue
                    else:
                        return {'error': error_str, 'sql': sql}
            else:
                if retries < max_retries:
                    sql = self.generator.fix_sql(question, sql, val_res['error'])
                    retries += 1
                else:
                    return {'error': val_res['error'], 'sql': sql}
        
        return {'error': "Max retries reached", 'sql': sql}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="Natural language question for the SQL database")
    args = parser.parse_args()

    pipeline = SQLQAPipeline()
    
    if args.query:
        q = args.query
    else:
        # Default fallback if no query is provided
        q = "How many customers subscribed in each year?"
        print(f"No query provided. Using default: {q}\n")

    res = pipeline.run(q)
    
    if res.get('error'):
        print(f"Error: {res['error']}")
    else:
        print(f"SQL: {res['sql']}")
        print(f"Summary: {res['summary']}")
        print("\nData:")
        print(res['result'])
