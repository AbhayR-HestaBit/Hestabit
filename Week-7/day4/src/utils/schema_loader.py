from sqlalchemy import create_engine, inspect, text
import pandas as pd

class SchemaLoader:
    def __init__(self, db_path='src/data/enterprise.db'):
        # using absolute path for safety if needed, but relative should work inside project
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')

    def get_schema(self):
        inspector = inspect(self.engine)
        schema = {}
        
        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                col_info = f"{col['name']}: {col['type']}"
                if col.get('primary_key'):
                    col_info += " (PRIMARY KEY)"
                columns.append(col_info)
            
            # get sample rows
            with self.engine.connect() as conn:
                res = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                sample_rows = res.fetchall()
                
            schema[table_name] = {
                'columns': columns,
                'sample_rows': [list(row) for row in sample_rows]
            }
        return schema

    def format_schema_for_prompt(self):
        schema = self.get_schema()
        output = []
        for table, info in schema.items():
            output.append(f"Table: {table}")
            for col in info['columns']:
                output.append(f"  - {col}")
            output.append(f"  Sample rows: {info['sample_rows']}")
            output.append("")
        return "\n".join(output)

    def get_table_names(self):
        return inspect(self.engine).get_table_names()

    def get_row_count(self, table_name):
        with self.engine.connect() as conn:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return res.scalar()

if __name__ == "__main__":
    loader = SchemaLoader()
    print("Schema for prompt:")
    print(loader.format_schema_for_prompt())
