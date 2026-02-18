import json
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from src.pipelines.context_builder import ContextBuilder
from src.generator.llm_client import LocalLLMClient, MockLLMClient

class QueryEngine:
    # coordinates receiving a query, retrieving information, and getting a final answer
    def __init__(self, config_path='src/config/model.yaml'):
        with open(config_path, 'r') as f:
            self.cfg = yaml.safe_load(f)
        self.builder = ContextBuilder()
        self.llm = None
        # ensure logs dir exists
        Path('src/logs').mkdir(parents=True, exist_ok=True)

    def retrieve_with_trace(self, query, k=5, filters=None):
        # searches the database and saves a trace log of what it found
        ctx_dict = self.builder.build(query, top_k=k, filters=filters)
        
        # log trace to jsonl
        trace = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_chunks": ctx_dict.get('num_chunks', 0),
            "sources": ctx_dict.get('sources', [])
        }
        with open('src/logs/retrieval_trace.jsonl', 'a') as f:
            f.write(json.dumps(trace) + "\n")
            
        return ctx_dict

    def retrieve(self, query, k=5, filters=None):
        return self.builder.build(query, top_k=k, filters=filters)

    def answer(self, query, k=5, filters=None):
        # uses the ai model to read the retrieved context and answer the question
        ctx_dict = self.retrieve_with_trace(query, k=k, filters=filters)
        if not ctx_dict['context']: return "no context found.", []
        
        prompt = self.builder.format_prompt(ctx_dict)
        
        if self.llm is None:
            try: self.llm = LocalLLMClient()
            except: self.llm = MockLLMClient()
            
        return self.llm.generate(prompt), ctx_dict['sources']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--no_llm", action="store_true")
    args = parser.parse_args()
    
    engine = QueryEngine()
    if args.no_llm:
        res_dict = engine.retrieve(args.query)
        print(f"Results for: {res_dict['query']}")
        print(f"Chunks found: {res_dict['num_chunks']}\n")
        print(res_dict['context'])
    else:
        ans, res = engine.answer(args.query)
        print(f"\nFinal Answer: {ans}")
