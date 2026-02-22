import json
import argparse
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional
from src.pipelines.context_builder import ContextBuilder
from src.generator.llm_client import LocalLLMClient, MockLLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryEngine:
    """
    Coordinates receiving a query, retrieving information, and getting a final answer from an LLM.
    """
    def __init__(self, config_path: str = 'src/config/model.yaml'):
        self.config_path = Path(config_path)
        self.cfg = self._load_config()
        try:
            self.builder = ContextBuilder()
        except Exception as e:
            logger.error(f"Failed to initialize ContextBuilder: {e}")
            raise
        
        self.llm: Optional[Any] = None
        # ensure logs dir exists
        try:
            Path('src/logs').mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create logs directory: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """Loads the YAML configuration file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}, using defaults.")
            return {}
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}

    def retrieve_with_trace(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Searches the database and saves a trace log of what it found."""
        try:
            ctx_dict = self.builder.build(query, top_k=k, filters=filters)
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return {"query": query, "context": "", "num_chunks": 0, "sources": []}
        
        # log trace to jsonl
        trace = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_chunks": ctx_dict.get('num_chunks', 0),
            "sources": ctx_dict.get('sources', [])
        }
        try:
            with open('src/logs/retrieval_trace.jsonl', 'a') as f:
                f.write(json.dumps(trace) + "\n")
        except Exception as e:
            logger.error(f"Failed to write retrieval trace: {e}")
            
        return ctx_dict

    def retrieve(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieves relevant context for a query."""
        try:
            return self.builder.build(query, top_k=k, filters=filters)
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return {"query": query, "context": "", "num_chunks": 0, "sources": []}

    def answer(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Any]]:
        """Uses the AI model to read the retrieved context and answer the question."""
        try:
            ctx_dict = self.retrieve_with_trace(query, k=k, filters=filters)
            if not ctx_dict.get('context'):
                logger.info("No context found for query.")
                return "no context found.", []
            
            prompt = self.builder.format_prompt(ctx_dict)
            
            if self.llm is None:
                try:
                    logger.info("Initializing LocalLLMClient...")
                    self.llm = LocalLLMClient()
                except Exception as e:
                    logger.warning(f"LocalLLMClient initialization failed: {e}. Falling back to MockLLMClient.")
                    self.llm = MockLLMClient()
                
            return self.llm.generate(prompt), ctx_dict.get('sources', [])
        except Exception as e:
            logger.error(f"Critical error in QueryEngine.answer: {e}")
            return "An error occurred while processing your request.", []

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--no_llm", action="store_true")
    args = parser.parse_args()
    
    engine = QueryEngine()
    if args.no_llm:
        res_dict = engine.retrieve(args.query)
        logger.info(f"Results for: {res_dict.get('query')}")
        logger.info(f"Chunks found: {res_dict.get('num_chunks', 0)}")
        print(f"\nContext:\n{res_dict.get('context', '')}")
    else:
        ans, res = engine.answer(args.query)
        print(f"\nFinal Answer: {ans}")
