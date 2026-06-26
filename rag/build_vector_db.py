"""
rag/build_vector_db.py — Build FAISS vector store from knowledge-base text files
"""

import os
import pickle
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
INDEX_DIR = Path(__file__).parent / "faiss_index"


def build_vector_db(force_rebuild: bool = False):
    """
    Load all .txt files from the data/ directory, split them into chunks,
    embed with SentenceTransformers, and store in a FAISS index.

    Returns the FAISS vectorstore.
    """
    index_file = INDEX_DIR / "index.faiss"

    # ── Lazy imports (heavy packages only needed when RAG is used) ──────────
    from langchain_community.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    # ── Return cached index if it exists ────────────────────────────────────
    if not force_rebuild and index_file.exists():
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        return FAISS.load_local(
            str(INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    # ── Load documents ───────────────────────────────────────────────────────
    docs = []
    txt_files = list(DATA_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(
            f"No .txt files found in {DATA_DIR}. "
            "Ensure the data/ directory contains knowledge-base files."
        )

    for fp in txt_files:
        try:
            loader = TextLoader(str(fp), encoding="utf-8")
            docs.extend(loader.load())
        except Exception as e:
            print(f"[RAG] Warning: could not load {fp.name}: {e}")

    # ── Split into chunks ────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(docs)

    # ── Create embeddings ────────────────────────────────────────────────────
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    # ── Build FAISS index ────────────────────────────────────────────────────
    vectorstore = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))

    return vectorstore
