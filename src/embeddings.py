# src/embeddings.py
import requests
from typing import List


class EmbeddingGenerator:
    """
    ChromaDB が期待する形式に合わせた
    Ollama embedding ラッパークラス
    """

    def __init__(self, model: str = "snowflake-arctic-embed"):
        self.model = model
        self.url = "http://localhost:11434/api/embeddings"

    def _embed(self, text: str) -> List[float]:
        """Ollama API を使って 1 文を embedding"""
        payload = {
            "model": self.model,
            "prompt": text
        }

        response = requests.post(self.url, json=payload)
        data = response.json()

        if "embedding" not in data:
            raise ValueError(f"Embedding API エラー: {data}")

        return data["embedding"]

    # ★ Chroma が必ず呼び出すメソッド
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数文書の embedding"""
        return [self._embed(t) for t in texts]

    # ★ クエリ用（検索時に使われる）
    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)
