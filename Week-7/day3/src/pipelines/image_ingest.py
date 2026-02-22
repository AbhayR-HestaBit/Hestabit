import os
import json
import uuid
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

class ImageIngestor:
    def __init__(self):
        # load blip once
        print("loading blip model...")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cpu")

    def load_images(self, folder='src/data/images/raw/'):
        path = Path(folder)
        supported = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        image_files = []
        
        for f in path.rglob('*'):
            if f.is_dir(): continue
            # unique_id based on path to avoid collisions
            rel_path = f.relative_to(path)
            unique_id = str(rel_path).replace('/', '_').replace(f.suffix, '')
            
            if f.suffix.lower() == '.pdf':
                print(f"converting pdf: {f.name}")
                pages = convert_from_path(f, dpi=150)
                for i, page in enumerate(pages):
                    img_id = f"{unique_id}_p{i+1}"
                    name = f"{img_id}.jpg"
                    save_path = path / name
                    page.save(save_path, 'JPEG')
                    image_files.append({'path': str(save_path), 'image_id': img_id})
            elif f.suffix.lower() in supported:
                image_files.append({'path': str(f), 'image_id': unique_id})
        return image_files

    def preprocess(self, image_path, image_id):
        img = Image.open(image_path).convert('RGB')
        w, h = img.size
        if max(w, h) > 1024:
            scale = 1024 / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)))
        
        processed_path = f"src/data/images/processed/{image_id}.jpg"
        img.save(processed_path)
        return img, processed_path

    def extract_ocr(self, img, image_id):
        # raw text
        text = pytesseract.image_to_string(img)
        # filtered data
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        words = []
        confidences = []
        for i, word in enumerate(data['text']):
            if int(data['conf'][i]) >= 60:
                words.append(word)
                confidences.append(int(data['conf'][i]))
        
        clean_text = " ".join(words).strip()
        result = {
            'image_id': image_id,
            'ocr_text': clean_text,
            'word_count': len(words),
            'avg_confidence': sum(confidences)/len(confidences) if confidences else 0
        }
        with open(f"src/data/images/ocr/{image_id}.json", 'w') as f:
            json.dump(result, f, indent=2)
        return result

    def generate_caption(self, img, image_id):
        inputs = self.processor(img, return_tensors="pt").to("cpu")
        out = self.model.generate(**inputs, max_new_tokens=100)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        
        result = {'image_id': image_id, 'caption': caption}
        with open(f"src/data/images/captions/{image_id}.json", 'w') as f:
            json.dump(result, f, indent=2)
        return result

    def run_all(self, folder='src/data/images/raw/'):
        files = self.load_images(folder)
        results = []
        for f in files:
            print(f"processing: {f['image_id']}")
            img, _ = self.preprocess(f['path'], f['image_id'])
            ocr = self.extract_ocr(img, f['image_id'])
            cap = self.generate_caption(img, f['image_id'])
            results.append({**f, **ocr, **cap})
        
        print(f"\nfinished processing {len(results)} images")
        for r in results:
            print(f"- {r['image_id']}: {r['caption'][:50]}...")
        return results

if __name__ == "__main__":
    ingestor = ImageIngestor()
    ingestor.run_all()
