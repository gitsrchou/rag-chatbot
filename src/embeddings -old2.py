"""
Embedding生成モジュール（Ollama版）
LangChain の Embeddings クラス互換で動作
"""

import requests
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import (
    EMBEDDING_CONFIG,
    API_RETRY_ATTEMPTS,
    API_RETRY_MIN_WAIT,
    API_RETRY_MAX_WAIT
)
from concurrent.futures import ThreadPoolExecutor


class OllamaEmbeddings:
    """LangChain の Embeddings クラス互換"""

    def __init__(self, model: str):
        self.model = model
        self.url = "http://localhost:11434/api/embeddings"

    def _embed(self, text: str) -> List[float]:
        payload = {
            "model": self.model,
            "prompt": text
        }
        response = requests.post(self.url, json=payload)
        data = response.json()

        # モデルによってキーが違うので両方対応
        if "embedding" in data:
            return data["embedding"]
        elif "embeddings" in data:
            return data["embeddings"]
        else:
            raise KeyError(f"Unexpected embedding response format: {data}")

    from concurrent.futures import ThreadPoolExecutor

    def embed_documents(self, texts):
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self._embed, texts))
        return results


    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


class EmbeddingGenerator:
    """Ollama Embedding API を使用した Embedding 生成クラス"""

    def __init__(self, model_name: str = None):
        self.model = model_name or EMBEDDING_CONFIG["model"]
        self.embeddings = OllamaEmbeddings(self.model)

    def get_embedding_function(self):
        """Chroma が期待する Embeddings クラスを返す"""
        return self.embeddings
