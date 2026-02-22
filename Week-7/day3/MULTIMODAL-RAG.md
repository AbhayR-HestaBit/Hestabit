# Multimodal RAG — Day 3

This document explains the image-based RAG capabilities added to the system.

## 1. Folder Structure (Day 3)
- `clip_embedder.py`: Interacts with the ViT-B-32 model to embed images and text.
- `image_ingest.py`: Reads the images, runs OCR and BLIP, and creates metadata files.
- `image_search.py`: Handles queries matching text to images or images to answers.
- `image_store.py`: FAISS vector index specifically for image embeddings.

## 2. Architecture
```text
      [User Query]
           |
    _______|_______
   |               |
[Text Search]    [Visual Search]
(Day 2 Hybrid)   (Day 3 CLIP)
   |               |
   |_______ _______|
           |
    [Context Builder]
           |
     [LLM API]
           |
       [Answer]
```

## 2. Models Used (All CPU)
- **CLIP (ViT-B-32):** Maps images and text into a shared 512-dimensional embedding space. This allows us to search for images using text ("Text-to-Image") and vice-versa, without manually labeling them. Runs efficiently on CPU.
- **BLIP (base):** Generates natural language captions (descriptions) for images. This makes visual data searchable by traditional text search as well.
- **Tesseract OCR:** Extracts printed/written text from diagrams, forms, and screenshots.

## 3. Tesseract OCR Setup
To use OCR, you must have the Tesseract binary installed on your system:
- **Ubuntu/Linux:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`
- **Windows:** Download installer and add to your PATH.

## 4. Query Modes
### Text-to-Image
`python3 -m src.retriever.image_search --mode text2img --query "diagram of underwriting"`

### Image-to-Image
`python3 -m src.retriever.image_search --mode img2img --image src/data/images/raw/my_sample.jpg`

### Image-to-Answer
`python3 -m src.retriever.image_search --mode img2ans --image src/data/images/raw/diag.jpg --query "summarize this"`

## 6. How Visual Ingestion & Indexing Works
1. **Reading Image**: `image_ingest.py` scans pixel data.
2. **Text Extraction**: Tesseract OCR finds and saves any readable words on the image.
3. **Caption Generation**: BLIP creates a plain english sentence describing the image.
4. **Vector Embedding**: CLIP turns the image into a 512-dimension numerical array (vector).
5. **Storage**: The vector is saved to `image_index.faiss` and the caption/OCR are saved to `image_metadata.json`.

## 7. How Retrieval Works
Since CLIP was trained on text-image pairs, a text query like "red car" produces a vector that mathematically matches the vector generated from an actual picture of a red car. `image_search.py` simply maps your query to a vector and performs a fast similarity search in the FAISS index to find the closest matching image.

## Minimal Code Snippet
**Generating Captions with BLIP:**
```python
# simple caption generation for images
inputs = self.blip_processor(raw_image, return_tensors="pt")
out = self.blip_model.generate(**inputs)
caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
```

## Commands for Day 3
Make sure the API Key is set in your `.env`.

```bash
source week7_env/bin/activate
# Ingest the images and run OCR/BLIP/CLIP
python3 -m src.pipelines.image_ingest

# Text-to-Image
python3 -m src.retriever.image_search --mode text2img --query "diagram of underwriting"

# Image-to-Answer
python3 -m src.retriever.image_search --mode img2ans --image src/data/images/raw/my_sample.jpg --query "summarize this"
```

## Screenshots
[Add Screenshot of Image Ingestion execution here]

[Add Screenshot of Image-to-Answer command here]

## 6. CPU Performance & Troubleshooting
- **CLIP Embedding:** ~2s per image.
- **BLIP Captioning:** ~10-15s per image.
- **OCR:** ~1-3s per image.

**Troubleshooting:**
- **"Tesseract not found":** Ensure `tesseract` is in your system PATH.
- **Slow Inference:** Check if `torch` was installed with the CPU-specific index-url.
- **Model Download:** The first run will download ~2GB of models. Ensure you have an internet connection.