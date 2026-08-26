from typing import Any, Dict, List, Optional
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.prompts import ChatPromptTemplate

from backend.database import supabase
from config import DEFAULT_FETCH_K, DEFAULT_K, DEFAULT_LAMBDA
from services.models import get_embedding_model, get_llm


def get_vectorstore() -> SupabaseVectorStore:
    return SupabaseVectorStore(
        client=supabase,
        embedding=get_embedding_model(),
        table_name="document_vectors",
        query_name="match_documents",
    )


def get_retriever(
    vectorstore: SupabaseVectorStore,
    user_id: str,
    k: int = DEFAULT_K,
):
    return vectorstore.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {
                "user_id": str(user_id),
            },
        },
    )


def format_chat_history(
    chat_history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if not chat_history:
        return "No previous conversation."

    lines = []
    for message in chat_history[-8:]:
        role = message.get("role", "user")
        content = (message.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Chanti AI: {content}")

    return "\n".join(lines) if lines else "No previous conversation."


def create_prompt():
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """You are Chanti AI, a helpful document intelligence assistant.

For document questions, answer ONLY from the supplied document context.
If the answer is not supported by the context, say exactly:
"I couldn't find the answer in the uploaded documents."

Do not invent citations, facts, page numbers, or document contents.

For ordinary greetings and capability questions, respond naturally.
Use conversation history to resolve follow-up references, but never use
conversation history as a substitute for missing document evidence.

Be clear, accurate and concise. Use headings, bullets or tables when useful.

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{chat_history}
""",
        ),
        ("human", "{question}"),
    ])


def build_retrieval_query(question: str, chat_history=None) -> str:
    if not chat_history:
        return question

    history = []
    for message in chat_history[-4:]:
        content = (message.get("content") or "").strip()
        if content:
            history.append(f"{message.get('role', 'user')}: {content}")

    if not history:
        return question

    return "Previous conversation:\n" + "\n".join(history) + "\n\nCurrent question:\n" + question


def _page_number(document) -> int:
    page = (getattr(document, "metadata", {}) or {}).get("page", 0)
    try:
        return int(page) + 1
    except (TypeError, ValueError):
        return 1


def _build_context(documents) -> str:
    if not documents:
        return "No relevant document context was retrieved."

    parts = []
    for index, document in enumerate(documents, start=1):
        metadata = getattr(document, "metadata", {}) or {}
        source = metadata.get("source") or metadata.get("filename") or "Unknown document"
        parts.append(
            f"SOURCE {index}\n"
            f"Document: {source}\n"
            f"Page: {_page_number(document)}\n\n"
            f"Content:\n{document.page_content}"
        )
    return "\n\n".join(parts)


def ask_question(
    vectorstore: SupabaseVectorStore,
    question: str,
    user_id: str,
    chat_history=None,
    k: int = DEFAULT_K,
):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", []

    retriever = get_retriever(vectorstore, user_id, k)
    documents = retriever.invoke(build_retrieval_query(question, chat_history))
    prompt = create_prompt()

    final_prompt = prompt.invoke({
        "context": _build_context(documents),
        "chat_history": format_chat_history(chat_history),
        "question": question,
    })

    response = get_llm().invoke(final_prompt)
    content = response.content

    if isinstance(content, list):
        content = "".join(str(part) for part in content)

    return str(content), documents


def delete_document_vectors(*, document_key: str, user_id: str) -> int:
    document_key = (document_key or "").strip()
    if not document_key:
        return 0

    response = (
        supabase.table("document_vectors")
        .delete()
        .contains("metadata", {
            "user_id": str(user_id),
            "document_key": str(document_key),
        })
        .execute()
    )

    return len(getattr(response, "data", []) or [])