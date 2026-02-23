import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.reranker import Reranker

# Configure logging
logger = logging.getLogger(__name__)

class ContextBuilder:
    # responsible for pulling together text and image results into a single context string
    def __init__(self):
        try:
            self.retriever = HybridRetriever()
            self.reranker = Reranker()
        except Exception as e:
            logger.error(f"Failed to initialize ContextBuilder components: {e}")
            raise

    def build(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_rerank: bool = True,
        use_mmr: bool = False,
    ) -> Dict[str, Any]:
        try:
            # 1. get candidates (retrieve more for reranking)
            candidates = self.retriever.retrieve(query, top_k=top_k * 3, filters=filters)
    
            if not candidates:
                logger.warning(f"No candidates found for query: {query[:50]}...")
                return {"context": "", "sources": [], "query": query, "num_chunks": 0}
    
            # 2. rerank with cross-encoder
            if use_rerank:
                candidates = self.reranker.rerank(query, candidates)
    
            # 3. mmr for diversity (optional)
            if use_mmr:
                try:
                    # get embeddings for mmr
                    query_emb = self.retriever.embedder.model.encode(query)
                    # re-embed candidates for mmr scoring
                    for c in candidates:
                        c["embedding"] = self.retriever.embedder.model.encode(c["text"])
                    candidates = self.reranker.rerank_with_mmr(
                        query_emb, candidates, top_k=top_k
                    )
                except Exception as mmr_err:
                    logger.error(f"MMR reranking failed: {mmr_err}. Falling back to top_k slice.")
                    candidates = candidates[:top_k]
            else:
                candidates = candidates[:top_k]
    
            # 4. build context string
            ctx_list = []
            sources = []
            for i, c in enumerate(candidates):
                src_info = f"Source: {c.get('source', 'Unknown')} | Page: {c.get('page', 'N/A')}"
                ctx_list.append(f"--- {src_info} ---\n{c.get('text', '')}")
                sources.append({"source": c.get("source"), "page": c.get("page", "N/A")})
    
            context_str = "\n\n".join(ctx_list)
            logger.info(f"Context built with {len(candidates)} chunks.")
    
            return {
                "context": context_str,
                "sources": sources,
                "query": query,
                "num_chunks": len(candidates),
            }
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return {"context": "", "sources": [], "query": query, "num_chunks": 0, "error": str(e)}

    def build_multimodal(self, query: str, image_path: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        try:
            # reuse text logic
            text_data = self.build(query, top_k=top_k)
            
            # add image context if search engine exists
            try:
                from src.retriever.image_search import ImageSearchEngine
                img_engine = ImageSearchEngine()
                
                if image_path:
                    img_results = img_engine.image_to_image(image_path, top_k=top_k)
                else:
                    img_results = img_engine.text_to_image(query, top_k=top_k)
                    
                img_ctx = "\n".join([f"Image: {r.get('image_id')} | Caption: {r.get('caption')}" for r in img_results])
                
                combined_ctx = f"{text_data['context']}\n\n[IMAGE CONTEXT]\n{img_ctx}"
                text_data['context'] = combined_ctx
                text_data['sources'].extend([{'source': r.get('image_id'), 'type': 'image'} for r in img_results])
            except Exception as img_err:
                logger.warning(f"Multimodal context expansion failed: {img_err}")
                
            return text_data
        except Exception as e:
            logger.error(f"Multimodal build failed: {e}")
            return {"context": "", "sources": [], "query": query, "num_chunks": 0}

    def format_prompt(self, ctx_dict: Dict[str, Any]) -> str:
        try:
            p_path = Path('src/prompts/rag_prompt.txt')
            if p_path.exists():
                template = p_path.read_text(encoding="utf-8")
            else:
                logger.info("Prompt template file missing, using default fallback.")
                template = "Context:\n{context}\n\nQuestion: {query}\nAnswer:"
            return template.format(context=ctx_dict.get('context', ''), query=ctx_dict.get('query', ''))
        except Exception as e:
            logger.error(f"Prompt formatting failed: {e}")
            return f"Context: {ctx_dict.get('context')}\n\nQuery: {ctx_dict.get('query')}"

if __name__ == "__main__":
    builder = ContextBuilder()
    q = "risk factors in investment"
    data = builder.build(q, top_k=2)
    print(f"context length: {len(data['context'])}")
    print(f"sources: {data['sources']}")
