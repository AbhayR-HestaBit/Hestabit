import base64
import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
import shutil
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.embeddings.embedder import Embedder
from src.evaluation.rag_eval import RAGEvaluator
from src.evaluation.self_reflect import SelfReflector
from src.generator.llm_client import LocalLLMClient
from src.memory.memory_store import ConversationMemory
from src.pipelines.context_builder import ContextBuilder
from src.pipelines.sql_pipeline import SQLQAPipeline
from src.retriever.image_search import ImageSearchEngine
from src.retriever.query_engine import QueryEngine
from src.utils.tracer import RequestTracer
from src.vectorstore.vector_manager import VectorStoreManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("week7_rag.api")


class AskRequest(BaseModel):
    query: str
    session_id: str = "default"
    top_k: int = 5
    filters: Dict[str, Any] = Field(default_factory=dict)
    use_rerank: bool = True


class AskImageRequest(BaseModel):
    query: str = ""
    image_base64: str = ""
    session_id: str = "default"
    mode: str = Field(default="text2image", pattern="^(text2image|img2img|img2ans)$")


class AskSQLRequest(BaseModel):
    question: str
    session_id: str = "default"
    max_retries: int = 2


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load all ai models into memory once when server starts
    logger.info("Starting Week7 RAG app lifespan initialisation")

    # Core components
    llm_client = LocalLLMClient()
    embedder = Embedder()
    vector_manager = VectorStoreManager()
    vector_manager.load()

    query_engine = QueryEngine()
    context_builder = ContextBuilder()
    image_engine = ImageSearchEngine()
    sql_pipeline = SQLQAPipeline()
    memory = ConversationMemory()
    rag_eval = RAGEvaluator()
    self_reflector = SelfReflector(llm_client)
    tracer = RequestTracer()

    app.state.llm_client = llm_client
    app.state.embedder = embedder
    app.state.vector_manager = vector_manager
    app.state.query_engine = query_engine
    app.state.context_builder = context_builder
    app.state.image_engine = image_engine
    app.state.sql_pipeline = sql_pipeline
    app.state.memory = memory
    app.state.rag_eval = rag_eval
    app.state.self_reflector = self_reflector
    app.state.tracer = tracer

    logger.info("Application startup complete")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info("Request %s %s %s", request_id, request.method, request.url.path)
    response = await call_next(request)
    logger.info("Request %s completed with status %s", request_id, response.status_code)
    return response


@app.get("/health")
async def health():
    components = {
        "rag": bool(getattr(app.state, "vector_manager", None) is not None),
        "image_rag": bool(getattr(app.state, "image_engine", None) is not None),
        "sql_qa": bool(getattr(app.state, "sql_pipeline", None) is not None),
        "memory": bool(getattr(app.state, "memory", None) is not None),
        "llm": bool(getattr(app.state, "llm_client", None) is not None),
    }
    return {"status": "ok", "components": components}


@app.get("/sessions")
async def list_sessions():
    return {"sessions": app.state.memory.list_sessions()}


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    app.state.memory.clear(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Add a new document to the RAG database dynamically
    raw_dir = Path("src/data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    file_path = raw_dir / file.filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        from src.pipelines.ingest import DocumentLoader
        from src.embeddings.embedder import Embedder
        from src.vectorstore.vector_manager import VectorStoreManager
        from src.retriever.bm25_index import BM25Index
        import json

        DocumentLoader().process_folder()
        Embedder().embed_all()
        
        vm = VectorStoreManager()
        vm.build_index()
        
        # update BM25
        all_chunks = []
        for f in Path('src/data/chunks/').glob('*.json'):
            with open(f, 'r') as f_in: all_chunks.extend(json.load(f_in))
        if all_chunks:
            BM25Index(all_chunks).save('src/vectorstore/bm25_index.pkl')
            
        # reload app state so dashboard sees the new docs immediately
        vm.load()
        app.state.vector_manager = vm
        app.state.query_engine = QueryEngine()
        app.state.context_builder = ContextBuilder()
        
        return {"status": "success", "message": f"Successfully ingested {file.filename}"}
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask(req: AskRequest, request: Request) -> Dict[str, Any]:
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    try:
        tracer = getattr(app.state, "tracer", RequestTracer())
        memory = getattr(app.state, "memory", ConversationMemory())
        reflector = getattr(app.state, "self_reflector", None)
        evaluator = getattr(app.state, "rag_eval", RAGEvaluator())
        builder = getattr(app.state, "context_builder", ContextBuilder())
        llm = getattr(app.state, "llm_client", LocalLLMClient())
    
        if reflector is None:
            reflector = SelfReflector(llm)
    
        tracer.log(rid, "received", req.model_dump())
    
        history_prefix = memory.format_history_for_prompt(req.session_id)
        ctx_dict = builder.build(
            req.query,
            top_k=req.top_k,
            filters=req.filters or None,
            use_rerank=req.use_rerank,
        )
        
        tracer.log(
            rid,
            "retrieval",
            {
                "num_chunks": ctx_dict.get("num_chunks", 0),
                "sources": ctx_dict.get("sources", []),
            },
        )
    
        if not ctx_dict.get("context"):
            logger.warning(f"No context found for query: {req.query}")
            return {
                "answer": "I'm sorry, I couldn't find any relevant information in the documents to answer that.",
                "sources": [],
                "session_id": req.session_id,
                "query_id": rid
            }
    
        context_for_llm = ctx_dict["context"]
        if history_prefix:
            context_for_llm = f"{history_prefix}\n\n{context_for_llm}"
    
        prompt = builder.format_prompt({"context": context_for_llm, "query": req.query})
        
        try:
            raw_answer = llm.generate(prompt)
            tracer.log(rid, "llm_raw_answer", {"answer_preview": raw_answer[:200] if raw_answer else ""})
            
            refined_answer = reflector.refine_if_needed(req.query, raw_answer, context_for_llm)
            tracer.log(rid, "refined_answer", {"answer_preview": refined_answer[:200]})
        except Exception as llm_exc:
            logger.error(f"LLM generation/refinement failed: {llm_exc}")
            refined_answer = "An error occurred while generating the answer. Please try again."
    
        # Evaluation is best-effort
        eval_result = {}
        try:
            eval_result = evaluator.evaluate_response(
                req.query,
                ctx_dict["context"],
                refined_answer,
                retrieval_scores=[],
            )
            tracer.log(rid, "evaluation", eval_result)
        except Exception as eval_exc:
            logger.error(f"Evaluation failed: {eval_exc}")
    
        # Update memory
        memory.add_turn(
            req.session_id,
            role="user",
            content=req.query,
            sources=[],
            modality="text",
        )
        memory.add_turn(
            req.session_id,
            role="assistant",
            content=refined_answer,
            sources=ctx_dict.get("sources", []),
            modality="text",
        )
    
        response = {
            "answer": refined_answer,
            "sources": ctx_dict.get("sources", []),
            "session_id": req.session_id,
            "query_id": rid,
            "faithfulness": eval_result.get("faithfulness"),
            "confidence": eval_result.get("confidence"),
            "hallucination_flagged": eval_result.get("hallucination_flagged"),
        }
        tracer.log(rid, "response", response)
        return response
    except Exception as e:
        logger.error(f"Error in /ask: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing RAG query.")


@app.post("/ask-image")
async def ask_image(req: AskImageRequest, request: Request):
    # handle image upload and image-related questions
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    tracer = getattr(app.state, "tracer", None)
    if tracer is None:
        tracer = RequestTracer()
        app.state.tracer = tracer
        
    memory = getattr(app.state, "memory", None)
    if memory is None:
        memory = ConversationMemory()
        app.state.memory = memory
        
    image_engine = getattr(app.state, "image_engine", None)
    if image_engine is None:
        image_engine = ImageSearchEngine()
        app.state.image_engine = image_engine
        
    evaluator = getattr(app.state, "rag_eval", None)
    if evaluator is None:
        evaluator = RAGEvaluator()
        app.state.rag_eval = evaluator

    tracer.log(rid, "received_image", req.model_dump())

    tmp_image_path: Optional[Path] = None
    if req.image_base64:
        try:
            raw = base64.b64decode(req.image_base64)
            tmp_image_path = Path("src/data/tmp_image.jpg")
            tmp_image_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_image_path.write_bytes(raw)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {exc}")

    mode = req.mode
    image_results: List[Dict] = []
    answer: Optional[str] = None
    sources: List[Dict] = []

    if mode == "text2image":
        image_results = image_engine.text_to_image(req.query)
    elif mode == "img2img":
        if not tmp_image_path:
            raise HTTPException(status_code=400, detail="image_base64 required for img2img")
        image_results = image_engine.image_to_image(str(tmp_image_path))
    elif mode == "img2ans":
        if not tmp_image_path:
            raise HTTPException(status_code=400, detail="image_base64 required for img2ans")
        answer = image_engine.image_to_answer(str(tmp_image_path), req.query)

    for r in image_results:
        src = {"source": r.get("image_id"), "type": "image"}
        sources.append(src)

    faithfulness = None
    confidence = None
    hallucination_flagged = None

    if mode == "img2ans" and answer is not None:
        # Build simple context from image results (captions + OCR)
        ctx_parts = []
        for r in image_results:
            ctx_parts.append(
                f"Image: {r.get('image_id')}\nCaption: {r.get('caption')}\nOCR: {r.get('ocr_text')}"
            )
        ctx = "\n\n".join(ctx_parts)
        eval_result = evaluator.evaluate_response(
            req.query, ctx, answer, retrieval_scores=[]
        )
        faithfulness = eval_result.get("faithfulness")
        confidence = eval_result.get("confidence")
        hallucination_flagged = eval_result.get("hallucination_flagged")

        memory.add_turn(
            req.session_id, role="user", content=req.query, sources=sources, modality="image"
        )
        memory.add_turn(
            req.session_id,
            role="assistant",
            content=answer,
            sources=sources,
            modality="image",
        )

    resp = {
        "answer": answer,
        "image_results": image_results,
        "sources": sources,
        "session_id": req.session_id,
        "faithfulness": faithfulness,
        "confidence": confidence,
        "hallucination_flagged": hallucination_flagged,
    }
    tracer.log(rid, "response_image", resp)
    return resp


@app.post("/ask-sql")
async def ask_sql(req: AskSQLRequest, request: Request):
    # convert natural language to sql and query the database
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    tracer = getattr(app.state, "tracer", None)
    if tracer is None:
        tracer = RequestTracer()
        app.state.tracer = tracer
        
    memory = getattr(app.state, "memory", None)
    if memory is None:
        memory = ConversationMemory()
        app.state.memory = memory
        
    sql_pipeline = getattr(app.state, "sql_pipeline", None)
    if sql_pipeline is None:
        sql_pipeline = SQLQAPipeline()
        app.state.sql_pipeline = sql_pipeline

    tracer.log(rid, "received_sql", req.model_dump())

    result = sql_pipeline.run(req.question, max_retries=req.max_retries)
    error = result.get("error")

    answer_text = result.get("summary") if not error else ""

    memory.add_turn(
        req.session_id, role="user", content=req.question, sources=[], modality="text"
    )
    memory.add_turn(
        req.session_id,
        role="assistant",
        content=answer_text or (error or ""),
        sources=[],
        modality="text",
    )

    rows = []
    if result.get("result") is not None:
        try:
            df = result["result"]
            rows = df.to_dict(orient="records")
        except Exception:
            rows = []

    resp = {
        "answer": answer_text,
        "sql": result.get("sql"),
        "result_rows": rows,
        "summary": result.get("summary"),
        "session_id": req.session_id,
        "error": error,
    }
    tracer.log(rid, "response_sql", resp)
    return resp

