# Week 7: RAG

## Folder Structure
```text
week7_rag/
├── src/
│   ├── config/
│   │   └── model.yaml
│   ├── data/
│   │   ├── chunks/
│   │   ├── cleaned/
│   │   ├── embeddings/
│   │   ├── images/
│   │   │   ├── raw/
│   │   │   ├── processed/
│   │   │   ├── ocr/
│   │   │   └── captions/
│   │   ├── raw/
│   │   └── enterprise.db
│   ├── deployment/
│   │   ├── app.py           
│   │   └── streamlit_app.py 
│   ├── embeddings/
│   │   ├── clip_embedder.py
│   │   ├── embedder.py
│   │   └── __init__.py
│   ├── evaluation/
│   │   ├── rag_eval.py      
│   │   ├── retrieval_eval.py
│   │   ├── self_reflect.py  
│   │   └── __init__.py
│   ├── generator/
│   │   ├── llm_client.py
│   │   ├── sql_generator.py
│   │   └── __init__.py
│   ├── logs/
│   │   ├── memory_*.json
│   │   ├── eval_log.jsonl
│   │   └── request_trace.jsonl
│   ├── memory/
│   │   ├── memory_store.py  
│   │   └── __init__.py
│   ├── pipelines/
│   │   ├── context_builder.py
│   │   ├── image_ingest.py
│   │   ├── ingest.py
│   │   ├── run_pipeline.py
│   │   ├── sql_pipeline.py
│   │   └── __init__.py
│   ├── prompts/
│   │   ├── rag_prompt.txt
│   │   └── sql_prompt.txt
│   ├── retriever/
│   │   ├── bm25_index.py
│   │   ├── hybrid_retriever.py
│   │   ├── image_search.py
│   │   ├── query_engine.py
│   │   ├── reranker.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── create_sample_db.py
│   │   ├── schema_loader.py
│   │   ├── sql_validator.py
│   │   ├── text_utils.py
│   │   ├── tracer.py
│   │   └── __init__.py
│   └── vectorstore/
│       ├── image_index.faiss
│       ├── image_metadata.json
│       ├── index.faiss
│       ├── bm25_index.pkl
│       └── vector_manager.py
└── tests/
    └── test_integration.py  
```

## Completed Tasks

### Day 1: Foundational Text RAG
- Ingestion Pipeline with PDF/DOCX/CSV/TXT files.
- Integrated BGE-small-en-v1.5 embeddings.
- Built VectorStoreManager using FAISS.
- Created run_pipeline.py CLI.

### Day 2: Advanced Retrieval Strategies
- BM25 Indexing for keyword-based search.
- Hybrid Retrieval (Semantic FAISS + Keyword BM25 using RRF fusion).
- Cross-Encoder Reranking using ms-marco-MiniLM-L-6-v2.
- MMR (Max Marginal Relevance) for context diversity.

### Day 3: Multimodal RAG
- OCR Integration via Tesseract to extract text from images.
- BLIP Captioning to describe visual data in natural language.
- CLIP Embeddings for a unified text-image vector space.
- Implemented Text-to-Image, Image-to-Image, and Image-to-Answer search modes.

### Day 4: SQL Question Answering (Text-to-SQL)
- Loaded 10,000 real customer records from `customers-10000.csv` into SQLite (`enterprise.db`, table: `customers`).
- Implemented read-only SQLAlchemy connections for safety.
- Built SQLValidator with syntax and safety checks (no DROP/DELETE).
- Automated schema loading into the LLM context so it understands all column names.
- Designed a self-correction retry loop if the SQL execution fails.

### Day 5: APIs, Streamlit UI, Memory, and Evaluation
- FastAPI Backend serving unified /ask, /ask-image, and /ask-sql endpoints.
- Modularized Streamlit App providing an interactive conversational frontend.
- API Driven Model Swap: Replaced the slow local Mistral GGUF model with OpenRouter (meta-llama/llama-3.3-70b-instruct) API for scalable, instant responses.
- Contextual Memory Store logging user/assistant turns safely as JSON.
- Evaluator system calculating Faithfulness and Hallucination metrics.
- Comprehensive request tracing and integration testing.
