import argparse
from PIL import Image
from src.embeddings.clip_embedder import CLIPEmbedder
from src.vectorstore.image_store import ImageVectorStore
from src.generator.llm_client import LocalLLMClient, MockLLMClient
from pathlib import Path

class ImageSearchEngine:
    def __init__(self):
        self.embedder = CLIPEmbedder()
        self.store = ImageVectorStore()
        self.llm = None

    def text_to_image(self, query, top_k=5, threshold=0.24):
        vec = self.embedder.embed_text(query)
        results = self.store.search(vec, k=top_k)
        return [r for r in results if r.get('score', 0) >= threshold]

    def image_to_image(self, img_path, top_k=5, threshold=0.24):
        img = Image.open(img_path).convert('RGB')
        vec = self.embedder.embed_image(img)
        results = self.store.search(vec, k=top_k)
        return [r for r in results if r.get('score', 0) >= threshold]

    def image_to_answer(self, img_path, question, threshold=0.24):
        results = self.image_to_image(img_path, top_k=3, threshold=threshold)
        if not results: return "No highly relevant visual context was found in the database to answer this question accurately."
        
        ctx = "\n".join([f"Image: {r['image_id']}\nCaption: {r['caption']}\nOCR: {r['ocr_text']}" for r in results])
        p_path = Path('src/prompts/rag_prompt.txt')
        template = p_path.read_text() if p_path.exists() else "{context}\n{query}"
        
        if self.llm is None:
            try: self.llm = LocalLLMClient()
            except: self.llm = MockLLMClient()
            
        full_ctx = f"[MULTIMODAL CONTEXT]\n{ctx}"
        return self.llm.generate(template.format(context=full_ctx, query=question))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=['text2img', 'img2img', 'img2ans'], required=True)
    parser.add_argument("--query", type=str)
    parser.add_argument("--image", type=str)
    args = parser.parse_args()
    
    engine = ImageSearchEngine()
    
    if args.mode == 'text2img':
        res = engine.text_to_image(args.query)
        for r in res: print(f"- {r['image_id']} (score: {r['score']:.4f}): {r['caption']}")
    elif args.mode == 'img2img':
        res = engine.image_to_image(args.image)
        for r in res: print(f"- {r['image_id']} (score: {r['score']:.4f}): {r['caption']}")
    elif args.mode == 'img2ans':
        ans = engine.image_to_answer(args.image, args.query)
        print(f"\n {ans}")
