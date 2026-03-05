from __future__ import annotations

import json
import os
from pathlib import Path

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
SESSIONS_FILE = Path("logs/ui_sessions.json")

st.set_page_config(page_title="Week 8 Local LLM UI", layout="wide")
st.title("Week 8 — Local LLM Streamlit UI")



def load_session_ids() -> list[str]:
    if SESSIONS_FILE.exists():
        try:
            data = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
            return sorted(list(data.keys()))
        except Exception as e:
            st.warning(f"Could not load session IDs: {e}")
            return []
    return []


with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["generate", "chat"])
    temperature = st.slider("temperature", 0.0, 1.5, 0.2, 0.1)
    top_p = st.slider("top_p", 0.1, 1.0, 0.9, 0.05)
    top_k = st.slider("top_k", 1, 100, 40, 1)
    max_tokens = st.slider("max_tokens", 16, 512, 128, 16)
    system_prompt = st.text_area("System prompt", "You are a helpful local medical assistant.")
    session_id = st.text_input("Session ID", "streamlit-session")

if mode == "generate":
    prompt = st.text_area("Prompt", height=220, placeholder="Enter your prompt here...")
    if st.button("Generate", type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Generating..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/generate",
                        json={
                            "prompt": prompt,
                            "temperature": temperature,
                            "top_p": top_p,
                            "top_k": top_k,
                            "max_tokens": max_tokens,
                        },
                        timeout=300,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    st.subheader("Response")
                    st.write(data.get("text", ""))
                    with st.expander("Raw API Metadata"):
                        st.json(data)
                except requests.exceptions.ConnectionError:
                    st.error(f"Failed to connect to API at {API_URL}. Is the server running?")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

else:
    message = st.text_area("Message", height=160, placeholder="Type your chat message...")
    if st.button("Send", type="primary"):
        if not message.strip():
            st.error("Please enter a message.")
        else:
            with st.spinner("Replying..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "session_id": session_id,
                            "system_prompt": system_prompt,
                            "message": message,
                            "temperature": temperature,
                            "top_p": top_p,
                            "top_k": top_k,
                            "max_tokens": max_tokens,
                        },
                        timeout=300,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    st.subheader("Assistant")
                    st.write(data.get("text", ""))
                    with st.expander("Raw API Metadata"):
                        st.json(data)
                except requests.exceptions.ConnectionError:
                    st.error(f"Failed to connect to API at {API_URL}. Is the server running?")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

st.divider()
st.caption("Tip: start the FastAPI server first, then launch this Streamlit UI.")
