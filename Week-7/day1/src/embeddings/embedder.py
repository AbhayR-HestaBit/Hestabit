import os
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

class Embedder:
    # this class converts raw text chunks into numerical vectors (embeddings)
    def __init__(self, model_name='BAAI/bge-small-en-v1.5', device='cpu'):
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = 32

    def embed_all(self, chunk_dir='src/data/chunks/', output_dir='src/data/embeddings/'):
        # loops through all text chunks, generates their vectors, and saves them
        chunk_path, output_path = Path(chunk_dir), Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for chunk_file in chunk_path.glob('*_chunks.json'):
            stem = chunk_file.name.replace('_chunks.json', '')
            
            emb_out_file = output_path / f"{stem}_embeddings.npy"
            if emb_out_file.exists():
                print(f"Skipping {stem}, embeddings already exist.")
                continue
                
            print(f"embedding: {stem}")
            with open(chunk_file, 'r') as f:
                chunks = json.load(f)
            
            texts = [c['text'] for c in chunks]
            embeddings = self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True)
            
            np.save(emb_out_file, embeddings)
            id_map = {i: c['chunk_id'] for i, c in enumerate(chunks)}
            with open(output_path / f"{stem}_id_map.json", 'w') as f:
                json.dump(id_map, f, indent=2)
            print(f"saved embeddings for {stem}")

if __name__ == "__main__":
    embedder = Embedder()
    embedder.embed_all()
