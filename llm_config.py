"""
LLM / Embedding 설정
=====================
환경변수 LLM_PROVIDER로 프로바이더를 선택합니다.
지원: ollama (기본), openai, claude, gemini
"""

import os

from dotenv import load_dotenv
from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")


class _Embeddings(OpenAIEmbeddings):
    """OpenAIEmbeddings에 embed_query/embed_documents를 추가한 래퍼."""

    def embed_query(self, text: str) -> list[float]:
        return self.embed_text(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed_texts(texts)

    async def aembed_query(self, text: str) -> list[float]:
        return await self.aembed_text(text)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self.aembed_texts(texts)


def get_llm():
    """LLM_PROVIDER에 따라 적절한 LLM을 반환합니다."""

    if LLM_PROVIDER == "openai":
        # pip install openai
        # 환경변수: OPENAI_API_KEY
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        return llm_factory(model)

    elif LLM_PROVIDER == "claude":
        # pip install anthropic
        # 환경변수: ANTHROPIC_API_KEY
        from anthropic import AsyncAnthropic

        model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return llm_factory(model, client=client)

    elif LLM_PROVIDER == "gemini":
        # pip install litellm
        # 환경변수: GEMINI_API_KEY
        model = os.getenv("LLM_MODEL", "gemini/gemini-2.0-flash")
        return llm_factory(model)

    else:  # ollama (기본)
        from openai import AsyncOpenAI

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
        model = os.getenv("LLM_MODEL", "qwen2.5:latest")
        client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        return llm_factory(model, client=client)


def get_embeddings():
    """임베딩 모델을 반환합니다.

    임베딩은 OpenAI 호환 API만 지원하므로,
    LLM이 Claude/Gemini여도 임베딩은 OpenAI 또는 Ollama를 사용합니다.
    """
    from openai import AsyncOpenAI

    if LLM_PROVIDER == "openai":
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    else:
        # Ollama 또는 다른 프로바이더 → Ollama 임베딩 사용
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
        client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    return _Embeddings(client=client, model=model)
