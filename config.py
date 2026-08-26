import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = os.getenv("CHROMA_DIR", str(BASE_DIR / "chromadb"))

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mistral-embed")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-small-2603")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
DEFAULT_K = int(os.getenv("DEFAULT_K", "4"))
DEFAULT_FETCH_K = int(os.getenv("DEFAULT_FETCH_K", "12"))
DEFAULT_LAMBDA = float(os.getenv("DEFAULT_LAMBDA", "0.5"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
MAX_FILES_PER_UPLOAD = int(os.getenv("MAX_FILES_PER_UPLOAD", "10"))
MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "4000"))

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def validate_settings(require_external: bool = True) -> None:
    required = {
        "MISTRAL_API_KEY": MISTRAL_API_KEY,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_ROLE_KEY,
    }
    if require_external:
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        raise RuntimeError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")