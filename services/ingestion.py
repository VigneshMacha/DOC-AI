import os
import tempfile
import uuid
from typing import Any, List, Tuple

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.database import supabase
from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)
from services.models import get_embedding_model


# =========================================================
# FILE HELPERS & LOADING
# =========================================================

def _save_upload_to_temp(uploaded_file) -> Tuple[str, str]:
    filename = (getattr(uploaded_file, "filename", None) or "document.pdf").strip()
    if not filename:
        filename = "document.pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        uploaded_file.file.seek(0)
        content = uploaded_file.file.read()
        if not content:
            raise ValueError(f"{filename} is empty.")
        temp_file.write(content)
        return temp_file.name, filename


def _load_pdf_text(temp_path: str, filename: str) -> List[Document]:
    documents = PyPDFLoader(temp_path).load()
    if not documents:
        return []

    cleaned = []
    for document in documents:
        text = (document.page_content or "").strip()
        metadata = dict(getattr(document, "metadata", None) or {})
        metadata["source"] = filename
        metadata["filename"] = filename

        if text:
            document.metadata = metadata
            cleaned.append(document)
    return cleaned


def _load_pdf_with_ocr(temp_path: str, filename: str) -> List[Document]:
    try:
        import fitz  # PyMuPDF
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "This PDF is scanned or image-only. OCR requires: pip install pymupdf pytesseract pillow"
        ) from exc

    tesseract_cmd = os.getenv("TESSERACT_CMD", "").strip()
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        pdf = fitz.open(temp_path)
    except Exception as exc:
        raise ValueError(f"Unable to open {filename} for OCR.") from exc

    documents = []
    try:
        for page_number, page in enumerate(pdf, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            text = pytesseract.image_to_string(image, config="--psm 3").strip()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "filename": filename,
                        "page": page_number - 1,
                        "ocr": True,
                    },
                )
            )
    finally:
        pdf.close()

    return documents


def load_pdf(uploaded_file) -> List[Document]:
    temp_path, filename = _save_upload_to_temp(uploaded_file)
    try:
        # Fast path: Native text-based PDF
        documents = _load_pdf_text(temp_path, filename)
        if documents:
            return documents

        # Fallback: Scanned/image-only PDF OCR
        documents = _load_pdf_with_ocr(temp_path, filename)
        if documents:
            return documents

        raise ValueError(
            f"'{filename}' does not contain readable text or OCR could not extract any content."
        )
    finally:
        try:
            os.remove(temp_path)
        except (FileNotFoundError, PermissionError):
            pass


# =========================================================
# CHUNKING & SUPABASE VECTOR STORE
# =========================================================

def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def create_vectorstore(chunks: List[Document]) -> SupabaseVectorStore:
    if not chunks:
        raise ValueError("No text chunks were generated.")

    return SupabaseVectorStore.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        client=supabase,
        table_name="document_vectors",
        query_name="match_documents",
    )


# =========================================================
# PRIMARY DOCUMENT PROCESSOR
# =========================================================

def process_documents(
    uploaded_files,
    user_id: str,
) -> Tuple[Any, int, int, List[str], List[str]]:
    """
    Ingests and embeds user PDFs into Supabase pgvector.

    Returns:
        (
            vectorstore,
            total_pages,
            total_chunks,
            filenames,
            document_keys,
        )
    """
    if uploaded_files is None:
        raise ValueError("No files were uploaded.")

    if isinstance(uploaded_files, (list, tuple)):
        files = list(uploaded_files)
    else:
        files = [uploaded_files]

    files = [f for f in files if f is not None and getattr(f, "filename", None)]
    if not files:
        raise ValueError("No valid PDF files provided.")

    all_documents = []
    filenames = []
    document_keys = []
    total_pages = 0

    for uploaded_file in files:
        filename = (uploaded_file.filename or "").strip()
        if not filename.lower().endswith(".pdf"):
            raise ValueError(f"Only PDF files are supported: {filename}")

        # Unique identifier per upload batch for scoped deletion
        document_key = str(uuid.uuid4())
        documents = load_pdf(uploaded_file)

        if not documents:
            raise ValueError(f"No readable text in {filename}")

        for doc in documents:
            meta = dict(getattr(doc, "metadata", None) or {})
            meta["user_id"] = str(user_id)
            meta["filename"] = filename
            meta["source"] = filename
            meta["document_key"] = document_key
            doc.metadata = meta

        all_documents.extend(documents)
        filenames.append(filename)
        document_keys.append(document_key)
        total_pages += len(documents)

    if not all_documents:
        raise ValueError("No readable PDF pages were found.")

    chunks = split_documents(all_documents)
    if not chunks:
        raise ValueError("No text chunks could be created.")

    # Explicitly ensure chunk-level tenant metadata
    for chunk in chunks:
        meta = dict(getattr(chunk, "metadata", None) or {})
        meta["user_id"] = str(user_id)
        chunk.metadata = meta

    vectorstore = create_vectorstore(chunks)

    return (
        vectorstore,
        total_pages,
        len(chunks),
        filenames,
        document_keys,
    )