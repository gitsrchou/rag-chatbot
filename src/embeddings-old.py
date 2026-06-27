"""
Embedding生成モジュール
Ollama のローカル Embedding API を使用してテキストのEmbeddingを生成
"""

import os
import requests
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import (
    EMBEDDING_CONFIG,
    API_RETRY_ATTEMPTS,
    API_RETRY_MIN_WAIT,
    API_RETRY_MAX_WAIT
)


class EmbeddingGenerator:
    """Ollama Embedding APIを使用したEmbedding生成クラス"""

    def __init__(self, model_name: str = None):
        """
        Args:
            model_name: 使用するOllamaのEmbeddingモデル名
        """
        self.model = model_name or EMBEDDING_CONFIG["model"]
        self.url = "http://localhost:11434/api/embeddings"

    def _embed(self, text: str) -> List[float]:
        """Ollama API に1件のテキストを投げてEmbeddingを取得"""
        payload = {
            "model": self.model,
            "prompt": text
        }

        response = requests.post(self.url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Ollama Embedding API エラー: {response.text}")

        data = response.json()
        return data["embedding"]

    @retry(
        stop=stop_after_attempt(API_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=API_RETRY_MIN_WAIT,
            max=API_RETRY_MAX_WAIT
        )
    )
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数テキストのEmbedding生成"""
        return [self._embed(t) for t in texts]

    @retry(
        stop=stop_after_attempt(API_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=API_RETRY_MIN_WAIT,
            max=API_RETRY_MAX_WAIT
        )
    )
    def embed_query(self, text: str) -> List[float]:
        """単一テキストのEmbedding生成"""
        return self._embed(text)

    def get_embedding_function(self):
        """
        LangChain の VectorStore 用に互換関数を返す
        """
        return self.embed_query
