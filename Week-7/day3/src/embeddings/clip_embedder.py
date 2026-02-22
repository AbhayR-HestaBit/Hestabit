import torch
import open_clip
import numpy as np
from PIL import Image
from pathlib import Path

class CLIPEmbedder:
    def __init__(self):
        print("loading clip model (vit-b-32)...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', pretrained='openai'
        )
        self.model = self.model.to('cpu')
        self.model.eval()
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')

    def embed_image(self, pil_image):
        img_tensor = self.preprocess(pil_image).unsqueeze(0)
        with torch.no_grad():
            vec = self.model.encode_image(img_tensor)
        # normalize
        vec /= vec.norm(dim=-1, keepdim=True)
        return vec.squeeze().numpy()

    def embed_text(self, text):
        tokens = self.tokenizer([text])
        with torch.no_grad():
            vec = self.model.encode_text(tokens)
        # normalize
        vec /= vec.norm(dim=-1, keepdim=True)
        return vec.squeeze().numpy()

    def embed_all_images(self, processed_dir='src/data/images/processed/', output_dir='src/data/images/embeddings/'):
        proc_path = Path(processed_dir)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        for f in proc_path.glob('*.jpg'):
            print(f"embedding image: {f.name}")
            img = Image.open(f).convert('RGB')
            vec = self.embed_image(img)
            np.save(out_path / f"{f.stem}.npy", vec)
        print("done embedding images.")

if __name__ == "__main__":
    embedder = CLIPEmbedder()
    embedder.embed_all_images()
