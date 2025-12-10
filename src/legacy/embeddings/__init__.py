"""
Embeddings generator

Document text to vector embedding conversion
Supports multiple providers: Ollama (default), OpenAI
"""

from .base import BaseEmbedder, EmbeddingError
from .ollama_embedder import OllamaEmbedder
from .openai_embedder import OpenAIEmbedder


def create_embedder(provider: str = "ollama", **kwargs) -> BaseEmbedder:
    """
    Embedder 팩토리 함수
    
    Args:
        provider: 임베딩 제공자 ("ollama" 또는 "openai")
        **kwargs: 각 embedder의 설정 파라미터
    
    Returns:
        BaseEmbedder 인스턴스
    
    Examples:
        # Ollama 사용 (기본)
        embedder = create_embedder("ollama", model="nomic-embed-text")
        
        # OpenAI 사용
        embedder = create_embedder("openai", api_key="sk-...", model="text-embedding-3-small")
    """
    if provider == "ollama":
        return OllamaEmbedder(**kwargs)
    elif provider == "openai":
        return OpenAIEmbedder(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'ollama' or 'openai'.")


# Backward compatibility
DocumentEmbedder = OllamaEmbedder  # 기본값은 Ollama

__all__ = [
    "BaseEmbedder",
    "EmbeddingError",
    "OllamaEmbedder",
    "OpenAIEmbedder",
    "create_embedder",
    "DocumentEmbedder",  # Deprecated, use create_embedder
]
