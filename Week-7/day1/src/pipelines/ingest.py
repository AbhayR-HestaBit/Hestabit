import os
import json
import uuid
import unicodedata
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# Configure logging
logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Handles loading, cleaning, and chunking documents from various formats (PDF, DOCX, TXT, CSV).
    """
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=lambda x: len(self.tokenizer.encode(x))
            )
        except Exception as e:
            logger.error(f"Failed to initialize tokenizer/splitter: {e}")
            raise

    def clean_text(self, text: str) -> str:
        """Normalizes and cleans text by removing control characters and extra whitespace."""
        if not text:
            return ""
        try:
            text = unicodedata.normalize('NFKC', text)
            text = "".join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
            return " ".join(text.split())
        except Exception as e:
            logger.warning(f"Error cleaning text: {e}")
            return text

    def load_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Loads a single file and extracts its text contents based on extension."""
        ext = file_path.suffix.lower()
        docs = []
        try:
            if ext == '.pdf':
                reader = PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    txt = page.extract_text()
                    if txt:
                        docs.append({'text': self.clean_text(txt), 'metadata': {'page': i+1, 'type': 'pdf'}})
            elif ext == '.docx':
                doc = Document(file_path)
                txt = "\n".join([p.text for p in doc.paragraphs])
                if txt:
                    docs.append({'text': self.clean_text(txt), 'metadata': {'page': 1, 'type': 'docx'}})
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    txt = f.read()
                if txt:
                    docs.append({'text': self.clean_text(txt), 'metadata': {'page': 1, 'type': 'txt'}})
            elif ext == '.csv':
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip')
                for i, row in df.iterrows():
                    docs.append({'text': self.clean_text(row.to_string()), 'metadata': {'page': i+1, 'type': 'csv'}})
            else:
                logger.warning(f"Unsupported file extension: {ext} for file {file_path}")
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            
        return docs

    def process_folder(self, input_dir: str = 'src/data/raw/', output_dir: str = 'src/data/chunks/') -> None:
        """Processes all files in a folder, load them, chunk them, and save as JSON."""
        input_path, output_path = Path(input_dir), Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create output directory {output_path}: {e}")
            return

        for file in input_path.glob('*'):
            if file.is_dir():
                continue
            chunks_out_file = output_path / f"{file.stem}_chunks.json"
            if chunks_out_file.exists():
                logger.info(f"Skipping {file.name}, chunks already exist.")
                continue
                
            logger.info(f"Processing file: {file.name}")
            try:
                docs = self.load_file(file)
                chunks = []
                for d in docs:
                    split_texts = self.splitter.split_text(d['text'])
                    for i, txt in enumerate(split_texts):
                        chunks.append({
                            'chunk_id': str(uuid.uuid4()),
                            'text': txt,
                            'metadata': {**d['metadata'], 'source': file.name, 'index': i}
                        })
                if chunks:
                    with open(chunks_out_file, 'w', encoding='utf-8') as f:
                        json.dump(chunks, f, indent=2, ensure_ascii=False)
                    logger.info(f"Successfully saved {len(chunks)} chunks for {file.name}")
            except Exception as e:
                logger.error(f"Failed to process file {file.name}: {e}")

if __name__ == "__main__":
    loader = DocumentLoader()
    loader.process_folder()
