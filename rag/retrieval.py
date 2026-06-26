"""
rag/retrieval.py — Retrieve context chunks from FAISS and query Gemini
"""

from __future__ import annotations

_vectorstore = None  # module-level cache


def _get_vectorstore(force_rebuild: bool = False):
    global _vectorstore
    if _vectorstore is None or force_rebuild:
        from rag.build_vector_db import build_vector_db
        _vectorstore = build_vector_db(force_rebuild=force_rebuild)
    return _vectorstore


def retrieve_context(query: str, k: int = 4) -> str:
    """
    Retrieve the top-k most relevant document chunks for a query.

    Returns a single string of concatenated context passages.
    """
    vs = _get_vectorstore()
    docs = vs.similarity_search(query, k=k)
    if not docs:
        return "No relevant information found in the knowledge base."
    return "\n\n---\n\n".join(d.page_content for d in docs)


def answer_question(question: str) -> tuple[str, str]:
    """
    Retrieve context for the question, then call Gemini to answer.

    Returns (answer, context) tuple.
    """
    context = retrieve_context(question)
    from ai.gemini_client import answer_civic_question
    answer = answer_civic_question(question, context)
    return answer, context


def rebuild_index() -> str:
    """Force a full rebuild of the FAISS vector store."""
    global _vectorstore
    _vectorstore = None
    _get_vectorstore(force_rebuild=True)
    return "Knowledge base rebuilt successfully."
