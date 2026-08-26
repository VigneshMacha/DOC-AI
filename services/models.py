from functools import lru_cache
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from config import EMBEDDING_MODEL, LLM_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> MistralAIEmbeddings:
    return MistralAIEmbeddings(model=EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_llm() -> ChatMistralAI:
    return ChatMistralAI(model=LLM_MODEL)