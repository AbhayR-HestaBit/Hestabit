from pathlib import Path
from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.reranker import Reranker

class ContextBuilder:
    # responsible for pulling together text and image results into a single context string
    def __init__(self):
        self.retriever = HybridRetriever()
        self.reranker = Reranker()

    def build(self, query, top_k=5, filters=None, use_rerank=True, use_mmr=False):
        # fetches text data from database, scores it, and builds a context block
        # 1. get candidates (retrieve more for reranking)
        candidates = self.retriever.retrieve(query, top_k=top_k*3, filters=filters)
        
        if not candidates:
            return {"context": "", "sources": [], "query": query}

        # 2. rerank with cross-encoder
        if use_rerank:
            candidates = self.reranker.rerank(query, candidates)

        # 3. mmr for diversity (optional)
        if use_mmr:
            # get embeddings for mmr
            query_emb = self.retriever.embedder.model.encode(query)
            # re-embed candidates for mmr scoring (simple & fast for small list)
            for c in candidates:
                c['embedding'] = self.retriever.embedder.model.encode(c['text'])
            candidates = self.reranker.rerank_with_mmr(query_emb, candidates, top_k=top_k)
        else:
            candidates = candidates[:top_k]

        # 4. build context string
        ctx_list = []
        sources = []
        for i, c in enumerate(candidates):
            src_info = f"Source: {c['source']} | Page: {c.get('page', 'N/A')}"
            ctx_list.append(f"--- {src_info} ---\n{c['text']}")
            sources.append({"source": c['source'], "page": c.get('page', 'N/A')})
            
        context_str = "\n\n".join(ctx_list)
        
        return {
            "context": context_str,
            "sources": sources,
            "query": query,
            "num_chunks": len(candidates)
        }

    def build_multimodal(self, query, image_path=None, top_k=5):
        # reuse Day 2 logic for text
        text_data = self.build(query, top_k=top_k)
        
        # add image context if search engine exists
        from src.retriever.image_search import ImageSearchEngine
        img_engine = ImageSearchEngine()
        
        if image_path:
            img_results = img_engine.image_to_image(image_path, top_k=top_k)
        else:
            img_results = img_engine.text_to_image(query, top_k=top_k)
            
        img_ctx = "\n".join([f"Image: {r['image_id']} | Caption: {r['caption']}" for r in img_results])
        
        combined_ctx = f"{text_data['context']}\n\n[IMAGE CONTEXT]\n{img_ctx}"
        text_data['context'] = combined_ctx
        text_data['sources'].extend([{'source': r['image_id'], 'type': 'image'} for r in img_results])
        
        return text_data

    def format_prompt(self, ctx_dict):
        # merges the context window with the prompt template
        p_path = Path('src/prompts/rag_prompt.txt')
        if p_path.exists():
            template = p_path.read_text()
        else:
            template = "Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        return template.format(context=ctx_dict['context'], query=ctx_dict['query'])

if __name__ == "__main__":
    builder = ContextBuilder()
    q = "risk factors in investment"
    data = builder.build(q, top_k=2)
    print(f"context length: {len(data['context'])}")
    print(f"sources: {data['sources']}")
