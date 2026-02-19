import os
import json
from pathlib import Path
from src.embeddings.embedder import Embedder
from src.vectorstore.vector_manager import VectorStoreManager
from src.retriever.bm25_index import BM25Index

class HybridRetriever:
    def __init__(self, semantic_weight=0.7, bm25_weight=0.3):
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        
        # init components
        self.embedder = Embedder()
        self.vm = VectorStoreManager()
        self.vm.load()
        
        bm25_path = 'src/vectorstore/bm25_index.pkl'
        if os.path.exists(bm25_path):
            self.bm25_index = BM25Index.load(bm25_path)
        else:
            self.bm25_index = None
            print("warning: bm25 index not found")

    def retrieve(self, query, top_k=5, filters=None):
        # 1. semantic search
        query_vec = self.embedder.model.encode(query)
        semantic_results = self.vm.search(query_vec, k=20)
        
        # 2. bm25 search
        bm25_results = []
        if self.bm25_index:
            bm25_results = self.bm25_index.search(query, top_k=20)
            
        # 3. rrf fusion
        fused_scores = {} # cid -> score
        
        for rank, res in enumerate(semantic_results):
            cid = res.get('chunk_id') or f"{res['source']}_{res['page']}_{res['text'][:30]}"
            fused_scores[cid] = self.semantic_weight / (rank + 60)
            
        for rank, res in enumerate(bm25_results):
            cid = res.get('chunk_id') or f"{res['source']}_{res['page']}_{res['text'][:30]}"
            fused_scores[cid] = fused_scores.get(cid, 0) + (self.bm25_weight / (rank + 60))
            
        # combine all candidates
        candidates = { (res.get('chunk_id') or f"{res['source']}_{res['page']}_{res['text'][:30]}"): res 
                      for res in semantic_results + bm25_results }
        
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
                if not match: continue
                
            final_results.append(res)
            
        # 5. check for fallback
        if len(final_results) < 2:
            print("warning: fallback triggered - results too low")
            return self.fallback_search(query, top_k)
            
        return final_results[:top_k]

    def fallback_search(self, query, top_k=5):
        # simple substring search
        query = query.lower()
        results = []
        if self.bm25_index:
            for chunk in self.bm25_index.chunks:
                if query in chunk['text'].lower():
                    results.append(chunk)
                    if len(results) >= top_k: break
        return results

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
