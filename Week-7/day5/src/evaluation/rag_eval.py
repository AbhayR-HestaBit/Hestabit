import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)


class RAGEvaluator:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        log_path: str = "src/logs/eval_log.jsonl",
    ) -> None:
        try:
            logger.info(f"Initializing RAGEvaluator with model: {model_name}")
            self.model = SentenceTransformer(model_name, device="cpu")
            self.log_path = Path(log_path)
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to initialize RAGEvaluator: {e}")
            raise

    def faithfulness_score(self, answer: str, context: str) -> float:
        try:
            answer = (answer or "").strip()
            context_lc = (context or "").lower()
            if not answer or not context_lc:
                return 0.0
    
            sentences = [s.strip() for s in answer.split(". ") if s.strip()]
            if not sentences:
                return 0.0
    
            matches = 0
            for sent in sentences:
                words = [w for w in sent.split() if w]
                if not words:
                    continue
    
                n = 6
                if len(words) < n:
                    ngrams = [" ".join(words)]
                else:
                    ngrams = [
                        " ".join(words[i : i + n]) for i in range(len(words) - n + 1)
                    ]
    
                found = any(ngram.lower() in context_lc for ngram in ngrams)
                if found:
                    matches += 1
    
            score = matches / max(len(sentences), 1)
            return float(max(0.0, min(1.0, score)))
        except Exception as e:
            logger.error(f"Error calculating faithfulness score: {e}")
            return 0.0

    def context_relevance_score(self, query: str, context: str) -> float:
        try:
            texts = [(query or "").strip(), (context or "").strip()]
            if not texts[0] or not texts[1]:
                return 0.0
            embeddings = self.model.encode(texts)
            sim = cosine_similarity(
                np.array([embeddings[0]]), np.array([embeddings[1]])
            )[0][0]
            # cosine similarity normalise to [0, 1]
            norm_sim = (sim + 1.0) / 2.0
            return float(max(0.0, min(1.0, norm_sim)))
        except Exception as e:
            logger.error(f"Error calculating context relevance: {e}")
            return 0.0

    def hallucination_flag(self, answer: str, context: str) -> Dict:
        # flags instances where the ai likely made up information
        answer = (answer or "").strip()
        context_lc = (context or "").lower()
        sentences = [s.strip() for s in answer.split(". ") if s.strip()]
        total = len(sentences)
        if total == 0:
            return {
                "flagged": True,
                "faithfulness": 0.0,
                "suspicious_sentences": [],
            }

        suspicious: List[str] = []
        faithful_count = 0
        n = 6

        for sent in sentences:
            words = [w for w in sent.split() if w]
            if not words:
                suspicious.append(sent)
                continue

            if len(words) < n:
                ngrams = [" ".join(words)]
            else:
                ngrams = [
                    " ".join(words[i : i + n]) for i in range(len(words) - n + 1)
                ]

            sent_match = any(ngram.lower() in context_lc for ngram in ngrams)
            sent_score = 1.0 if sent_match else 0.0
            if sent_score < 0.3:
                suspicious.append(sent)
            if sent_match:
                faithful_count += 1

        faith = faithful_count / max(total, 1)
        flagged = faith < 0.5
        return {
            "flagged": flagged,
            "faithfulness": float(max(0.0, min(1.0, faith))),
            "suspicious_sentences": suspicious,
        }

    def confidence_score(self, retrieval_scores: List[float]) -> float:
        if not retrieval_scores:
            return 0.0
        scores = sorted(retrieval_scores, reverse=True)[:3]
        mean_score = sum(scores) / len(scores)
        return float(max(0.0, min(1.0, mean_score)))

    def evaluate_response(
        self,
        query: str,
        context: str,
        answer: str,
        retrieval_scores: List[float],
    ) -> Dict[str, Any]:
        try:
            faith = self.faithfulness_score(answer, context)
            ctx_rel = self.context_relevance_score(query, context)
            conf = self.confidence_score(retrieval_scores)
            halluc = self.hallucination_flag(answer, context)
    
            record = {
                "query": query,
                "answer": answer,
                "context_snippet": context[:500] if context else "",
                "faithfulness": faith,
                "context_relevance": ctx_rel,
                "confidence": conf,
                "hallucination_flagged": halluc["flagged"],
                "suspicious_sentences": halluc["suspicious_sentences"],
                "eval_timestamp": datetime.now(timezone.utc).isoformat(),
            }
    
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
            logger.info(f"Evaluation complete for query: {query[:50]}...")
            return record
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {"error": str(e)}

