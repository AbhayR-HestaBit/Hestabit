import os
import json
import uuid
import logging
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)

class ImageIngestor:
    def __init__(self, model_id: str = "Salesforce/blip-image-captioning-base"):
        try:
            logger.info(f"Loading BLIP model: {model_id}")
            self.processor = BlipProcessor.from_pretrained(model_id)
            self.model = BlipForConditionalGeneration.from_pretrained(model_id).to("cpu")
        except Exception as e:
            logger.error(f"Failed to load BLIP model: {e}")
            raise

    def load_images(self, folder: str = 'src/data/images/raw/') -> List[Dict[str, str]]:
        path = Path(folder)
        supported = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        image_files = []
        
        try:
            for f in path.rglob('*'):
                if f.is_dir():
                    continue
                # unique_id based on path to avoid collisions
                rel_path = f.relative_to(path)
                unique_id = str(rel_path).replace('/', '_').replace(f.suffix, '')
                
                if f.suffix.lower() == '.pdf':
                    try:
                        logger.info(f"Converting PDF to images: {f.name}")
                        pages = convert_from_path(f, dpi=150)
                        for i, page in enumerate(pages):
                            img_id = f"{unique_id}_p{i+1}"
                            name = f"{img_id}.jpg"
                            save_path = path / name
                            page.save(save_path, 'JPEG')
                            image_files.append({'path': str(save_path), 'image_id': img_id})
                    except Exception as e:
                        logger.error(f"Failed to convert PDF {f.name}: {e}")
                elif f.suffix.lower() in supported:
                    image_files.append({'path': str(f), 'image_id': unique_id})
        except Exception as e:
            logger.error(f"Error scanning folder {folder}: {e}")
            
        return image_files

    def preprocess(self, image_path: str, image_id: str) -> Tuple[Optional[Image.Image], str]:
        try:
            img = Image.open(image_path).convert('RGB')
            w, h = img.size
            if max(w, h) > 1024:
                scale = 1024 / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)))
            
            processed_path = f"src/data/images/processed/{image_id}.jpg"
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            img.save(processed_path)
            return img, processed_path
        except Exception as e:
            logger.error(f"Failed to preprocess image {image_id}: {e}")
            return None, ""

    def extract_ocr(self, img: Image.Image, image_id: str) -> Dict[str, Any]:
        try:
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
            save_path = f"src/data/images/ocr/{image_id}.json"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            return result
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_id}: {e}")
            return {'image_id': image_id, 'ocr_text': "", 'word_count': 0, 'avg_confidence': 0}

    def generate_caption(self, img: Image.Image, image_id: str) -> Dict[str, Any]:
        try:
            inputs = self.processor(img, return_tensors="pt").to("cpu")
            out = self.model.generate(**inputs, max_new_tokens=100)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            result = {'image_id': image_id, 'caption': caption}
            save_path = f"src/data/images/captions/{image_id}.json"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            return result
        except Exception as e:
            logger.error(f"Caption generation failed for {image_id}: {e}")
            return {'image_id': image_id, 'caption': ""}

    def run_all(self, folder: str = 'src/data/images/raw/') -> List[Dict[str, Any]]:
        files = self.load_images(folder)
        results = []
        for f in files:
            img_id = f.get('image_id', 'unknown')
            logger.info(f"Processing image: {img_id}")
            try:
                img, _ = self.preprocess(f['path'], img_id)
                if img is None:
                    continue
                ocr = self.extract_ocr(img, img_id)
                cap = self.generate_caption(img, img_id)
                results.append({**f, **ocr, **cap})
            except Exception as e:
                logger.error(f"Pipeline failed for {img_id}: {e}")
        
        logger.info(f"Finished processing {len(results)} images.")
        for r in results:
            logger.debug(f"- {r['image_id']}: {r.get('caption', '')[:50]}...")
        return results

if __name__ == "__main__":
    ingestor = ImageIngestor()
    ingestor.run_all()
