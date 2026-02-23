import logging
from sqlalchemy import create_engine, text
import pandas as pd
from typing import Dict, Any, Optional

from src.generator.llm_client import LocalLLMClient
from src.utils.schema_loader import SchemaLoader
from src.generator.sql_generator import SQLGenerator
from src.utils.sql_validator import SQLValidator

# Configure logging
logger = logging.getLogger(__name__)

class SQLQAPipeline:
    def __init__(self, db_path: str = 'src/data/enterprise.db'):
        try:
            self.db_path = db_path
            self.loader = SchemaLoader(db_path)
            self.llm = LocalLLMClient()
            self.generator = SQLGenerator(self.llm, self.loader)
            self.validator = SQLValidator(known_tables=self.loader.get_table_names())
            
            # Read-only engine
            logger.info(f"Initializing SQL pipeline with database: {db_path}")
            self.engine = create_engine(
                f'sqlite:///file:{db_path}?mode=ro&uri=true',
                connect_args={'check_same_thread': False}
            )
        except Exception as e:
            logger.error(f"Failed to initialize SQLQAPipeline: {e}")
            raise

    def run(self, question: str, max_retries: int = 2) -> Dict[str, Any]:
        retries = 0
        try:
            sql = self.generator.generate(question)
        except Exception as e:
            logger.error(f"Initial SQL generation failed: {e}")
            return {'error': f"Failed to generate SQL: {e}", 'sql': ""}
        
        while retries <= max_retries:
            logger.info(f"Attempt {retries + 1}/{max_retries + 1} for question: {question[:50]}...")
            try:
                val_res = self.validator.validate(sql)
                if val_res.get('valid'):
                    try:
                        with self.engine.connect() as conn:
                            res = conn.execute(text(sql))
                            df = pd.DataFrame(res.fetchall(), columns=res.keys())
                        
                        logger.info(f"SQL executed successfully. Returned {len(df)} rows.")
                        
                        # summarize
                        summary_prompt = (
                            f"[INST] Question: {question}\n"
                            f"SQL Result:\n{df.to_string(max_rows=20)}\n"
                            "Summarize the findings in 2-3 natural sentences. [/INST]"
                        )
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
                        logger.warning(f"SQL execution error on attempt {retries + 1}: {error_str}")
                        if retries < max_retries:
                            sql = self.generator.fix_sql(question, sql, error_str)
                            retries += 1
                            continue
                        else:
                            return {'error': f"SQL Error: {error_str}", 'sql': sql}
                else:
                    val_error = val_res.get('error', 'Unknown validation error')
                    logger.warning(f"SQL validation failed: {val_error}")
                    if retries < max_retries:
                        sql = self.generator.fix_sql(question, sql, val_error)
                        retries += 1
                    else:
                        return {'error': f"Validation Error: {val_error}", 'sql': sql}
            except Exception as e:
                logger.error(f"Unexpected error in SQL pipeline: {e}")
                return {'error': f"Unexpected Error: {e}", 'sql': sql}
        
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
