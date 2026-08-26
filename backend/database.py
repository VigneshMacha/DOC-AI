import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing from environment")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is missing from environment")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

DOCUMENTS_TABLE = os.getenv("DOCUMENTS_TABLE", "documents")
CONVERSATIONS_TABLE = os.getenv("CONVERSATIONS_TABLE", "conversations")
MESSAGES_TABLE = os.getenv("MESSAGES_TABLE", "messages")


def _rows(response: Any) -> List[Dict[str, Any]]:
    return list(getattr(response, "data", None) or [])


def save_document(
    user_id: str,
    filename: str,
    page_count: int = 0,
    chunk_count: int = 0,
    document_key: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "user_id": str(user_id),
        "filename": (filename or "").strip(),
        "page_count": int(page_count or 0),
        "chunk_count": int(chunk_count or 0),
    }
    if document_key:
        payload["document_key"] = str(document_key)

    response = supabase.table(DOCUMENTS_TABLE).insert(payload).execute()
    rows = _rows(response)
    return rows[0] if rows else payload


def get_user_documents(user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(DOCUMENTS_TABLE)
        .select("*")
        .eq("user_id", str(user_id))
        .order("created_at", desc=True)
        .execute()
    )
    return _rows(response)


def get_document_record(user_id: str, document_id: str) -> Optional[Dict[str, Any]]:
    response = (
        supabase.table(DOCUMENTS_TABLE)
        .select("*")
        .eq("id", str(document_id))
        .eq("user_id", str(user_id))
        .limit(1)
        .execute()
    )
    rows = _rows(response)
    return rows[0] if rows else None


def delete_document_record(user_id: str, document_id: str) -> Optional[Dict[str, Any]]:
    response = (
        supabase.table(DOCUMENTS_TABLE)
        .delete()
        .eq("id", str(document_id))
        .eq("user_id", str(user_id))
        .select("*")
        .execute()
    )
    rows = _rows(response)
    return rows[0] if rows else None


def create_conversation(user_id: str, title: str = "New Conversation") -> Dict[str, Any]:
    payload = {
        "user_id": str(user_id),
        "title": (title or "New Conversation").strip()[:120],
    }
    response = supabase.table(CONVERSATIONS_TABLE).insert(payload).execute()
    rows = _rows(response)
    if not rows:
        raise RuntimeError("Conversation could not be created")
    return rows[0]


def get_user_conversations(user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(CONVERSATIONS_TABLE)
        .select("*")
        .eq("user_id", str(user_id))
        .order("created_at", desc=True)
        .execute()
    )
    return _rows(response)


def get_conversation(user_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
    response = (
        supabase.table(CONVERSATIONS_TABLE)
        .select("*")
        .eq("id", str(conversation_id))
        .eq("user_id", str(user_id))
        .limit(1)
        .execute()
    )
    rows = _rows(response)
    return rows[0] if rows else None


def delete_conversation(user_id: str, conversation_id: str) -> bool:
    conversation = get_conversation(user_id, conversation_id)
    if not conversation:
        return False

    supabase.table(MESSAGES_TABLE).delete().eq("conversation_id", str(conversation_id)).eq("user_id", str(user_id)).execute()
    supabase.table(CONVERSATIONS_TABLE).delete().eq("id", str(conversation_id)).eq("user_id", str(user_id)).execute()
    return True


def save_message(conversation_id: str, user_id: str, role: str, content: str) -> Dict[str, Any]:
    if role not in {"user", "assistant", "system"}:
        raise ValueError("Invalid message role")

    payload = {
        "conversation_id": str(conversation_id),
        "user_id": str(user_id),
        "role": role,
        "content": content,
    }
    response = supabase.table(MESSAGES_TABLE).insert(payload).execute()
    rows = _rows(response)
    if not rows:
        raise RuntimeError("Message could not be saved")
    return rows[0]


def get_messages(conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
    response = (
        supabase.table(MESSAGES_TABLE)
        .select("*")
        .eq("conversation_id", str(conversation_id))
        .eq("user_id", str(user_id))
        .order("created_at", desc=False)
        .execute()
    )
    return _rows(response)