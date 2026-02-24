import argparse
import logging
from PIL import Image
from src.embeddings.clip_embedder import CLIPEmbedder
from src.vectorstore.image_store import ImageVectorStore
from src.generator.llm_client import LocalLLMClient, MockLLMClient
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class ImageSearchEngine:
    def __init__(self):
        try:
            self.embedder = CLIPEmbedder()
            self.store = ImageVectorStore()
            self.llm = None
        except Exception as e:
            logger.error(f"Failed to initialize ImageSearchEngine components: {e}")
            raise

    def text_to_image(self, query: str, top_k: int = 5, threshold: float = 0.24) -> List[Dict[str, Any]]:
        try:
            vec = self.embedder.embed_text(query)
            results = self.store.search(vec, k=top_k)
            filtered = [r for r in results if r.get('score', 0) >= threshold]
            logger.info(f"Text-to-image search found {len(filtered)} results above threshold {threshold}.")
            return filtered
        except Exception as e:
            logger.error(f"Error during text-to-image search: {e}")
            return []

    def image_to_image(self, img_path: str, top_k: int = 5, threshold: float = 0.24) -> List[Dict[str, Any]]:
        try:
            img = Image.open(img_path).convert('RGB')
            vec = self.embedder.embed_image(img)
            results = self.store.search(vec, k=top_k)
            filtered = [r for r in results if r.get('score', 0) >= threshold]
            logger.info(f"Image-to-image search found {len(filtered)} results above threshold {threshold}.")
            return filtered
        except Exception as e:
            logger.error(f"Error during image-to-image search: {e}")
            return []

    def image_to_answer(self, img_path: str, question: str, threshold: float = 0.24) -> str:

        try:
            results = self.image_to_image(img_path, top_k=3, threshold=threshold)
            if not results:
                logger.warning("No highly relevant visual context found for answering.")
                return "No highly relevant visual context was found in the database to answer this question accurately."
            
            ctx = "\n".join([f"Image: {r.get('image_id')}\nCaption: {r.get('caption')}\nOCR: {r.get('ocr_text')}" for r in results])
            p_path = Path('src/prompts/rag_prompt.txt')
            template = p_path.read_text(encoding="utf-8") if p_path.exists() else "{context}\n{query}"
            
            if self.llm is None:
                try:
                    self.llm = LocalLLMClient()
                    logger.info("LocalLLMClient initialized for image-to-answer.")
                except Exception as e:
                    logger.warning(f"Failed to load LocalLLMClient: {e}. Falling back to MockLLMClient.")
                    self.llm = MockLLMClient()
                
            full_ctx = f"[MULTIMODAL CONTEXT]\n{ctx}"
            formatted_prompt = template.format(context=full_ctx, query=question)
            return self.llm.generate(formatted_prompt)
        except Exception as e:
            logger.error(f"Error during image-to-answer process: {e}")
            return f"An error occurred while processing your visual query: {e}"

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
