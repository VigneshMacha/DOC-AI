import logging
import os
from typing import List, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.auth import (
    AuthServiceUnavailable,
    EmailNotConfirmed,
    InvalidCredentials,
    signup_user,
    login_user,
    logout_user,
    get_current_user,
    set_auth_cookie,
    clear_auth_cookie,
)
from backend.database import (
    save_document,
    get_user_documents,
    create_conversation,
    get_user_conversations,
    get_conversation,
    delete_conversation,
    get_document_record,
    delete_document_record,
    save_message,
    get_messages,
)
from services.ingestion import process_documents
from services.rag import (
    ask_question,
    get_vectorstore,
    delete_document_vectors,
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("chanti")

app = FastAPI(
    title="Chanti AI",
    description="AI Document Intelligence and RAG Assistant",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

vectorstore = None


def _user_id(user) -> str:
    return str(user.id)


def _safe_page(document) -> int:
    metadata = getattr(document, "metadata", None) or {}
    page = metadata.get("page", 0)
    try:
        return int(page) + 1
    except (TypeError, ValueError):
        return 1


def _source_list(documents) -> list:
    sources = []
    seen = set()
    for document in documents or []:
        metadata = getattr(document, "metadata", None) or {}
        source = metadata.get("source") or metadata.get("filename") or "Unknown"
        page = _safe_page(document)
        key = (str(source), page)
        if key in seen:
            continue
        seen.add(key)
        sources.append({"source": str(source), "page": page})
    return sources


def get_dashboard_context(
    user,
    conversation_id: Optional[str] = None,
    messages=None,
    answer=None,
    question=None,
    sources=None,
    error=None,
):
    user_id = _user_id(user)

    try:
        conversations = get_user_conversations(user_id)
    except Exception:
        logger.exception("CONVERSATION LOAD ERROR")
        conversations = []

    try:
        documents = get_user_documents(user_id)
    except Exception:
        logger.exception("DOCUMENT LOAD ERROR")
        documents = []

    total_chunks = sum(int(doc.get("chunk_count", 0) or 0) for doc in documents)
    filenames = [doc.get("filename") for doc in documents if doc.get("filename")]

    return {
        "user": user,
        "uploaded": bool(documents),
        "document_count": len(documents),
        "chunk_count": total_chunks,
        "documents": documents,
        "filenames": filenames,
        "conversations": conversations,
        "conversation_id": conversation_id,
        "messages": messages or [],
        "answer": answer,
        "question": question,
        "sources": sources or [],
        "error": error,
    }


def _render(request: Request, user, **kwargs):
    context = get_dashboard_context(user, **kwargs)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@app.on_event("startup")
async def startup():
    global vectorstore
    try:
        vectorstore = get_vectorstore()
        logger.info("Chanti AI vector store initialized.")
    except Exception:
        logger.exception("VECTORSTORE STARTUP ERROR")
        vectorstore = None


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None})


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request=request, name="signup.html", context={"error": None})


@app.post("/signup")
async def signup(request: Request, email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    email = email.strip().lower()
    if password != confirm_password:
        return templates.TemplateResponse(request=request, name="signup.html", context={"error": "Passwords do not match.", "email": email}, status_code=400)
    if len(password) < 6:
        return templates.TemplateResponse(request=request, name="signup.html", context={"error": "Password must be at least 6 characters.", "email": email}, status_code=400)

    try:
        response = signup_user(email, password)
        if response.user is None:
            return templates.TemplateResponse(request=request, name="signup.html", context={"error": "Unable to create account.", "email": email}, status_code=400)

        if response.session is None:
            return templates.TemplateResponse(request=request, name="login.html", context={"error": "Account created. Please verify your email before logging in.", "email": email}, status_code=200)

        redirect = RedirectResponse("/", status_code=303)
        set_auth_cookie(redirect, response.session.access_token)
        return redirect
    except Exception:
        logger.exception("SIGNUP ERROR")
        return templates.TemplateResponse(request=request, name="signup.html", context={"error": "Unable to create account. Check details and retry.", "email": email}, status_code=400)


@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    email = email.strip().lower()
    try:
        response = login_user(email, password)
        redirect = RedirectResponse("/", status_code=303)
        set_auth_cookie(redirect, response.session.access_token)
        return redirect
    except (EmailNotConfirmed, InvalidCredentials, AuthServiceUnavailable) as exc:
        msg = "Authentication failed."
        if isinstance(exc, EmailNotConfirmed):
            msg = "Please verify your email before logging in."
        elif isinstance(exc, InvalidCredentials):
            msg = "Invalid email or password."
        elif isinstance(exc, AuthServiceUnavailable):
            msg = "Auth service temporarily unavailable. Try again shortly."
        return templates.TemplateResponse(request=request, name="login.html", context={"error": msg, "email": email}, status_code=401)
    except Exception:
        logger.exception("LOGIN ERROR")
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Sign in failed. Please try again.", "email": email}, status_code=500)


@app.post("/logout")
async def logout(request: Request):
    access_token = request.cookies.get("access_token")
    try:
        logout_user(access_token)
    except Exception:
        logger.exception("LOGOUT ERROR")
    redirect = RedirectResponse("/login", status_code=303)
    clear_auth_cookie(redirect)
    return redirect


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return _render(request, user)


@app.post("/new-chat")
async def new_chat(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    conversation = create_conversation(user_id=_user_id(user), title="New Conversation")
    return RedirectResponse(f"/chat/{conversation['id']}", status_code=303)


@app.get("/chat/{conversation_id}", response_class=HTMLResponse)
async def open_chat(request: Request, conversation_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    user_id = _user_id(user)
    try:
        conversation = get_conversation(user_id, conversation_id)
        if not conversation:
            return RedirectResponse("/", status_code=303)

        messages = get_messages(conversation_id, user_id)
        context = get_dashboard_context(user, conversation_id=conversation_id, messages=messages)
        context["current_chat"] = conversation
        return templates.TemplateResponse(request=request, name="index.html", context=context)
    except Exception:
        logger.exception("OPEN CHAT ERROR")
        return _render(request, user, conversation_id=conversation_id, error="Unable to open conversation.")


@app.post("/upload", response_class=HTMLResponse)
async def upload_documents(request: Request, files: List[UploadFile] = File(...)):
    global vectorstore
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    valid_files = [f for f in files if f and f.filename]
    if not valid_files:
        return _render(request, user, error="Please upload at least one PDF.")
    if any(not f.filename.lower().endswith(".pdf") for f in valid_files):
        return _render(request, user, error="Only PDF documents are supported.")

    try:
        user_id = _user_id(user)
        vectorstore, total_pages, total_chunks, filenames, document_keys = process_documents(valid_files, user_id)

        file_count = len(filenames)
        base_pages = total_pages // file_count
        page_rem = total_pages % file_count
        base_chunks = total_chunks // file_count
        chunk_rem = total_chunks % file_count

        for i, (fn, dkey) in enumerate(zip(filenames, document_keys)):
            fp = base_pages + (1 if i < page_rem else 0)
            fc = base_chunks + (1 if i < chunk_rem else 0)
            save_document(user_id=user_id, filename=fn, page_count=fp, chunk_count=fc, document_key=dkey)

        return _render(request, user)
    except Exception:
        logger.exception("UPLOAD ERROR")
        return _render(request, user, error="Document processing failed. Verify PDF structure and try again.")


@app.post("/documents/delete")
async def delete_document(request: Request, document_id: str = Form(""), filename: str = Form("")):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    user_id = _user_id(user)
    doc_id = (document_id or "").strip()
    if not doc_id:
        return _render(request, user, error="Invalid document ID.")

    try:
        record = get_document_record(user_id, doc_id)
        if not record:
            return _render(request, user, error="Document record not found.")

        document_key = (record.get("document_key") or "").strip()
        if document_key:
            delete_document_vectors(document_key=document_key, user_id=user_id)

        delete_document_record(user_id, doc_id)
        return RedirectResponse("/", status_code=303)
    except Exception:
        logger.exception("DOCUMENT DELETE ERROR")
        return _render(request, user, error="Could not delete document.")


@app.post("/chat/{conversation_id}/delete")
async def delete_chat(request: Request, conversation_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    try:
        delete_conversation(_user_id(user), conversation_id)
    except Exception:
        logger.exception("CHAT DELETE ERROR")
    return RedirectResponse("/", status_code=303)


@app.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, question: str = Form(...), conversation_id: str = Form("")):
    global vectorstore
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    user_id = _user_id(user)
    question = question.strip()
    if not question:
        return RedirectResponse(f"/chat/{conversation_id}" if conversation_id else "/", status_code=303)

    if len(question) > 4000:
        return _render(request, user, conversation_id=conversation_id, question=question, error="Question exceeded maximum character limit.")

    try:
        if vectorstore is None:
            vectorstore = get_vectorstore()

        if conversation_id:
            conv = get_conversation(user_id, conversation_id)
            if not conv:
                return RedirectResponse("/", status_code=303)
        else:
            conv = create_conversation(user_id, question[:60])
            conversation_id = str(conv["id"])

        history = get_messages(conversation_id, user_id)
        answer, docs = ask_question(vectorstore, question, user_id, chat_history=history)

        save_message(conversation_id, user_id, "user", question)
        save_message(conversation_id, user_id, "assistant", answer)

        sources = _source_list(docs)
        messages = get_messages(conversation_id, user_id)

        context = get_dashboard_context(
            user,
            conversation_id=conversation_id,
            messages=messages,
            answer=answer,
            question=question,
            sources=sources,
        )
        context["current_chat"] = get_conversation(user_id, conversation_id)
        return templates.TemplateResponse(request=request, name="index.html", context=context)
    except Exception:
        logger.exception("ASK ERROR")
        return _render(request, user, conversation_id=conversation_id, question=question, error="Failed to generate an answer. Please retry.")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Chanti AI"}