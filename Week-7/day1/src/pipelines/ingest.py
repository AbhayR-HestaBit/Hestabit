import os
import json
import uuid
import unicodedata
import pandas as pd
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

class DocumentLoader:
    def __init__(self, chunk_size=600, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=lambda x: len(self.tokenizer.encode(x))
        )

    def clean_text(self, text):
        if not text: return ""
        text = unicodedata.normalize('NFKC', text)
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
        return " ".join(text.split())

    def load_file(self, file_path):
        ext = file_path.suffix.lower()
        docs = []
        if ext == '.pdf':
            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt: docs.append({'text': self.clean_text(txt), 'metadata': {'page': i+1, 'type': 'pdf'}})
        elif ext == '.docx':
            doc = Document(file_path)
            txt = "\n".join([p.text for p in doc.paragraphs])
            if txt: docs.append({'text': self.clean_text(txt), 'metadata': {'page': 1, 'type': 'docx'}})
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                txt = f.read()
            if txt: docs.append({'text': self.clean_text(txt), 'metadata': {'page': 1, 'type': 'txt'}})
        elif ext == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip')
            for i, row in df.iterrows():
                docs.append({'text': self.clean_text(row.to_string()), 'metadata': {'page': i+1, 'type': 'csv'}})
        return docs

    def process_folder(self, input_dir='src/data/raw/', output_dir='src/data/chunks/'):
        input_path, output_path = Path(input_dir), Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file in input_path.glob('*'):
            if file.is_dir(): continue
            chunks_out_file = output_path / f"{file.stem}_chunks.json"
            if chunks_out_file.exists():
                print(f"Skipping {file.name}, chunks already exist.")
                continue
                
            print(f"loading: {file.name}")
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
                with open(chunks_out_file, 'w') as f:
                    json.dump(chunks, f, indent=2)
                print(f"saved {len(chunks)} chunks for {file.name}")

if __name__ == "__main__":
    loader = DocumentLoader()
    loader.process_folder()
