import numpy as np
from sentence_transformers import CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

class Reranker:
    def __init__(self):
        # load cross-encoder on cpu
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')

    def rerank(self, query, candidates, batch_size=16):
        if not candidates: return []
        
        # pairs for cross-encoding
        pairs = [[query, c['text']] for c in candidates]
        scores = self.model.predict(pairs, batch_size=batch_size)
        
        # add scores and sort
        for i, score in enumerate(scores):
            candidates[i]['rerank_score'] = float(score)
            
        return sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)

    def rerank_with_mmr(self, query_emb, candidates, lambda_=0.5, top_k=5):
        """
        max marginal relevance to ensure diversity.
        query_emb: vector for the query
        candidates: list of dicts with 'embedding' key (numpy array)
        """
        if not candidates: return []
        
        # ensure we have embeddings for candidates
        # for simplistic MMR, we assume they are already there or we provide them
        # in day 2, we can collect them from the FAISS manager if needed
        # but let's assume they are passed or handled in context_builder
        
        selected = []
        remaining = list(candidates)
        
        # if no embeddings provided, just return top_k
        if 'embedding' not in remaining[0]:
            return remaining[:top_k]

        while len(selected) < top_k and remaining:
            scores = []
            for r in remaining:
                # relevance (sim to query)
                rel = cosine_similarity(query_emb.reshape(1,-1), r['embedding'].reshape(1,-1))[0][0]
                
                # redundancy (max sim to selected)
                if not selected:
                    red = 0
                else:
                    red = max([cosine_similarity(r['embedding'].reshape(1,-1), s['embedding'].reshape(1,-1))[0][0] for s in selected])
                
                mmr_score = lambda_ * rel - (1 - lambda_) * red
                scores.append(mmr_score)
            
            # pick best
            best_idx = np.argmax(scores)
            selected.append(remaining.pop(best_idx))
            
        return selected
