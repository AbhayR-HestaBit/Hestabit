import json
import uuid

import httpx
import pandas as pd
import streamlit as st

import os

API_BASE = "http://localhost:8000"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

def get_session_id() -> str:
    # returns unique identifier for the current user session
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


def main():
    st.set_page_config(page_title="Week 7 RAG Capstone", layout="wide")
    st.title("Week 7 RAG")

    session_id = get_session_id()

    with st.sidebar:
        st.subheader("Session")
        session_id = st.text_input("Session ID", value=session_id)
        st.session_state.session_id = session_id

        mode = st.radio(
            "Mode",
            options=["Text RAG", "Image RAG", "SQL QA"],
            index=0,
        )
        top_k = st.slider("Top-K", min_value=1, max_value=10, value=5)
        use_rerank = st.checkbox("Use Reranking", value=True)
        show_debug = st.checkbox("Show Debug Info", value=False)

        st.divider()
        st.subheader("Add Knowledge")
        upload_file = st.file_uploader(
            "Upload new documents", 
            type=["pdf", "txt", "docx", "csv"],
            help="Upload a file to add it to the RAG knowledge base. The system will ingest it automatically."
        )
        if upload_file is not None:
            if st.button("Ingest File"):
                with st.spinner(f"Ingesting {upload_file.name}... this might take a minute."):
                    try:
                        files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type)}
                        resp = httpx.post(f"{API_BASE}/upload", files=files, timeout=300.0)
                        
                        if resp.status_code == 200:
                            st.success(f"Successfully added {upload_file.name} to the database!")
                        else:
                            st.error(f"Failed: {resp.text}")
                    except Exception as exc:
                        st.error(f"Error during ingestion: {exc}")

        st.divider()
        if st.button("Clear Memory"):
            try:
                httpx.delete(f"{API_BASE}/sessions/{session_id}", timeout=10.0)
                st.session_state.chat_history = []
                st.success("Memory cleared!")
            except Exception as exc:
                st.warning(f"Failed to clear memory: {exc}")

    if mode == "Text RAG":
        run_text_rag(session_id, top_k, use_rerank, show_debug)
    elif mode == "Image RAG":
        run_image_rag(session_id, top_k, show_debug)
    else:
        run_sql_qa(session_id, show_debug)


def run_text_rag(session_id: str, top_k: int, use_rerank: bool, show_debug: bool):
    # handles generic text questions using memory and vector db
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    query = st.chat_input("Ask a question about your documents...")
    if not query:
        return

    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    payload = {
        "query": query,
        "session_id": session_id,
        "top_k": top_k,
        "filters": {},
        "use_rerank": use_rerank,
    }

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            resp = httpx.post(f"{API_BASE}/ask", json=payload, timeout=60.0)
            data = resp.json()
            answer = data.get("answer", "")
            placeholder.markdown(answer)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )

            with st.expander("Sources"):
                for src in data.get("sources", []):
                    st.write(f"- {src}")

            cols = st.columns(3)
            cols[0].metric("Faithfulness", f"{data.get('faithfulness', 0):.2f}")
            cols[1].metric("Confidence", f"{data.get('confidence', 0):.2f}")
            cols[2].metric(
                "Hallucination",
                "Yes" if data.get("hallucination_flagged") else "No",
            )

            if show_debug:
                st.subheader("Raw Response")
                st.code(json.dumps(data, indent=2), language="json")
        except Exception as exc:
            placeholder.markdown(f"Error calling API: {exc}")


def run_image_rag(session_id: str, top_k: int, show_debug: bool):
    # handles uploading images and answering questions based on image content
    st.subheader("Image RAG")
    uploaded = st.file_uploader(
        "Upload an image", type=["png", "jpg", "jpeg", "pdf"]
    )
    question = st.text_input("Optional question for Image to Answer")
    mode = st.selectbox(
        "Image Mode",
        options=["text to image", "image to image", "image to answer"],
        index=0,
    )

    mode_map = {
        "text to image": "text2image",
        "image to image": "img2img",
        "image to answer": "img2ans",
    }
    api_mode = mode_map[mode]

    if st.button("Search"):
        image_b64 = ""
        if uploaded is not None:
            image_b64 = base64.b64encode(uploaded.read()).decode("utf-8")

        payload = {
            "query": question or "",
            "image_base64": image_b64,
            "session_id": session_id,
            "mode": api_mode,
        }

        try:
            resp = httpx.post(f"{API_BASE}/ask-image", json=payload, timeout=60.0)
            data = resp.json()

            if api_mode == "img2ans":
                st.subheader("Answer")
                st.write(data.get("answer", ""))

            st.subheader("Results")
            results = data.get("image_results", [])
            cols = st.columns(3)
            for i, r in enumerate(results):
                col = cols[i % 3]
                with col:
                    # Make path absolute so it works no matter where streamlit was launched
                    img_path = r.get("path")
                    if img_path:
                        abs_img_path = os.path.join(PROJECT_ROOT, img_path)
                        if os.path.exists(abs_img_path):
                            st.image(abs_img_path, caption=r.get("caption"))
                        else:
                            st.warning(f"Image file not found: {img_path}")
                    st.caption(r.get("ocr_text", "")[:120])

            if show_debug:
                st.subheader("Raw Response")
                st.code(json.dumps(data, indent=2), language="json")
        except Exception as exc:
            st.error(f"Error calling /ask-image: {exc}")


def run_sql_qa(session_id: str, show_debug: bool):
    # translates user questions into sql to query the database
    st.subheader("SQL Question Answering")
    question = st.text_input("Ask a question about the database")
    if st.button("Run SQL QA") and question:
        payload = {
            "question": question,
            "session_id": session_id,
            "max_retries": 2,
        }
        try:
            resp = httpx.post(f"{API_BASE}/ask-sql", json=payload, timeout=60.0)
            data = resp.json()

            st.subheader("Generated SQL")
            st.code(data.get("sql", ""), language="sql")

            rows = data.get("result_rows") or []
            if rows:
                df = pd.DataFrame(rows)
                st.subheader("Result Table")
                st.dataframe(df)

            if data.get("summary"):
                st.info(data["summary"])

            if show_debug:
                st.subheader("Raw Response")
                st.code(json.dumps(data, indent=2), language="json")
        except Exception as exc:
            st.error(f"Error calling /ask-sql: {exc}")


if __name__ == "__main__":
    import base64

    main()

