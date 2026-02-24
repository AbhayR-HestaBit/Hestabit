import torch
import open_clip
import numpy as np
import logging
from PIL import Image
from pathlib import Path
from typing import Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class CLIPEmbedder:
    def __init__(self, model_name: str = 'ViT-B-32', pretrained: str = 'openai'):
        try:
            logger.info(f"Loading CLIP model ({model_name})...")
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                model_name, pretrained=pretrained
            )
            self.model = self.model.to('cpu')
            self.model.eval()
            self.tokenizer = open_clip.get_tokenizer(model_name)
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise

    def embed_image(self, pil_image: Image.Image) -> np.ndarray:
        try:
            img_tensor = self.preprocess(pil_image).unsqueeze(0)
            with torch.no_grad():
                vec = self.model.encode_image(img_tensor)
            # normalize
            vec /= vec.norm(dim=-1, keepdim=True)
            return vec.squeeze().numpy()
        except Exception as e:
            logger.error(f"Error embedding image: {e}")
            return np.zeros(512)  # Return zero vector on failure

    def embed_text(self, text: str) -> np.ndarray:
        try:
            tokens = self.tokenizer([text])
            with torch.no_grad():
                vec = self.model.encode_text(tokens)
            # normalize
            vec /= vec.norm(dim=-1, keepdim=True)
            return vec.squeeze().numpy()
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            return np.zeros(512)

    def embed_all_images(self, processed_dir: str = 'src/data/images/processed/', output_dir: str = 'src/data/images/embeddings/') -> None:
        proc_path = Path(processed_dir)
        out_path = Path(output_dir)
        try:
            out_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create output directory {out_path}: {e}")
            return
            
        for f in proc_path.glob('*.jpg'):
            try:
                logger.info(f"Embedding image: {f.name}")
                img = Image.open(f).convert('RGB')
                vec = self.embed_image(img)
                np.save(out_path / f"{f.stem}.npy", vec)
            except Exception as e:
                logger.error(f"Failed to process image {f.name}: {e}")
        logger.info("Batch image embedding complete.")

if __name__ == "__main__":
    embedder = CLIPEmbedder()
    embedder.embed_all_images()
