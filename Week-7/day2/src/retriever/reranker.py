import numpy as np
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)

class Reranker:
    """
    Handles reranking of retrieved candidates using Cross-Encoders or Maximal Marginal Relevance (MMR).
    """
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2', device: str = 'cpu'):
        try:
            logger.info(f"Loading CrossEncoder model: {model_name} on {device}")
            self.model = CrossEncoder(model_name, device=device)
        except Exception as e:
            logger.error(f"Failed to load CrossEncoder model: {e}")
            raise

    def rerank(self, query: str, candidates: List[Dict[str, Any]], batch_size: int = 16) -> List[Dict[str, Any]]:
        """Reranks candidates using a cross-encoder model based on query relevance."""
        if not candidates:
            return []
        
        try:
            # pairs for cross-encoding
            pairs = [[query, c.get('text', '')] for c in candidates]
            logger.debug(f"Predicting scores for {len(pairs)} candidate pairs.")
            scores = self.model.predict(pairs, batch_size=batch_size)
            
            # add scores and sort
            for i, score in enumerate(scores):
                candidates[i]['rerank_score'] = float(score)
                
            sorted_candidates = sorted(candidates, key=lambda x: x.get('rerank_score', 0.0), reverse=True)
            logger.info(f"Reranked {len(candidates)} candidates.")
            return sorted_candidates
        except Exception as e:
            logger.error(f"Error during cross-encoder reranking: {e}")
            return candidates  # Return original if reranking fails

    def rerank_with_mmr(self, query_emb: np.ndarray, candidates: List[Dict[str, Any]], lambda_: float = 0.5, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance (MMR) to ensure diversity among top results.
        query_emb: vector for the query
        candidates: list of dicts with 'embedding' key (numpy array)
        """
        if not candidates:
            return []
        
        try:
            selected: List[Dict[str, Any]] = []
            remaining = list(candidates)
            
            # if no embeddings provided, just return top_k
            if not remaining or 'embedding' not in remaining[0]:
                logger.warning("No embeddings found in candidates; returning top_k without MMR.")
                return remaining[:top_k]

            while len(selected) < top_k and remaining:
                scores = []
                for r in remaining:
                    # relevance (sim to query)
                    rel = cosine_similarity(query_emb.reshape(1, -1), r['embedding'].reshape(1, -1))[0][0]
                    
                    # redundancy (max sim to selected)
                    if not selected:
                        red = 0.0
                    else:
                        red = max([cosine_similarity(r['embedding'].reshape(1, -1), s['embedding'].reshape(1, -1))[0][0] for s in selected])
                    
                    mmr_score = lambda_ * rel - (1 - lambda_) * red
                    scores.append(mmr_score)
                
                # pick best
                best_idx = np.argmax(scores)
                selected.append(remaining.pop(best_idx))
                
            logger.info(f"MMR selected {len(selected)} diverse candidates.")
            return selected
        except Exception as e:
            logger.error(f"Error during MMR reranking: {e}")
            return candidates[:top_k]
