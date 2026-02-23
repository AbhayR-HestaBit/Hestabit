import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from src.embeddings.embedder import Embedder
from src.vectorstore.vector_manager import VectorStoreManager
from src.retriever.bm25_index import BM25Index

# Configure logging
logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Combines semantic search and BM25 using Reciprocal Rank Fusion (RRF) for improved retrieval accuracy.
    """
    def __init__(self, semantic_weight: float = 0.7, bm25_weight: float = 0.3):
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        
        try:
            # init components
            self.embedder = Embedder()
            self.vm = VectorStoreManager()
            self.vm.load()
            
            bm25_path = 'src/vectorstore/bm25_index.pkl'
            if os.path.exists(bm25_path):
                self.bm25_index = BM25Index.load(bm25_path)
                logger.info(f"Loaded BM25 index from {bm25_path}")
            else:
                self.bm25_index = None
                logger.warning("BM25 index not found; semantic search only.")
        except Exception as e:
            logger.error(f"Failed to initialize HybridRetriever components: {e}")
            raise

    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Performs hybrid retrieval using RRF fusion and optional filtering."""
        try:
            # 1. semantic search
            query_vec = self.embedder.model.encode(query)
            semantic_results = self.vm.search(query_vec, k=20)
            
            # 2. bm25 search
            bm25_results = []
            if self.bm25_index:
                bm25_results = self.bm25_index.search(query, top_k=20)
                
            # 3. rrf fusion
            fused_scores: Dict[str, float] = {} # cid -> score
            
            def get_cid(res: Dict[str, Any]) -> str:
                return res.get('chunk_id') or f"{res.get('source', 'unknown')}_{res.get('page', 0)}_{res.get('text', '')[:30]}"

            for rank, res in enumerate(semantic_results):
                cid = get_cid(res)
                fused_scores[cid] = self.semantic_weight / (rank + 60)
                
            for rank, res in enumerate(bm25_results):
                cid = get_cid(res)
                fused_scores[cid] = fused_scores.get(cid, 0.0) + (self.bm25_weight / (rank + 60))
                
            # combine all unique candidates
            candidates = { get_cid(res): res for res in semantic_results + bm25_results }
            
            # sort by fused score
            final_results = []
            for cid, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True):
                res = candidates[cid].copy()
                res['rrf_score'] = score
                
                # 4. apply filters
                if filters:
                    match = True
                    for k, v in filters.items():
                        if res.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue
                    
                final_results.append(res)
                
            # 5. check for fallback
            if len(final_results) < 1:
                logger.warning("No results found; triggering fallback substring search.")
                return self.fallback_search(query, top_k)
                
            logger.info(f"Hybrid retrieval found {len(final_results)} candidates for query.")
            return final_results[:top_k]
        except Exception as e:
            logger.error(f"Error during hybrid retrieval: {e}")
            return []

    def fallback_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Simple substring search as a fallback when indexed results are insufficient."""
        query_lower = query.lower()
        results = []
        try:
            if self.bm25_index and hasattr(self.bm25_index, 'chunks'):
                for chunk in self.bm25_index.chunks:
                    if query_lower in chunk.get('text', '').lower():
                        results.append(chunk)
                        if len(results) >= top_k:
                            break
            return results
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []

if __name__ == "__main__":
    hr = HybridRetriever()
    q = "What are the sample trends?"
    res = hr.retrieve(q, top_k=3)
    
    print(f"query: {q}\n")
    for i, r in enumerate(res):
        print(f"result {i+1}:")
        print(f"source: {r['source']} | page: {r['page']}")
        print(f"text: {r['text'][:100]}...")
        print("-" * 30)
