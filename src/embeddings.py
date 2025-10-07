"""
Embedding生成モジュール
Google Embedding APIを使用してテキストのEmbeddingを生成
"""

import os
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import EMBEDDING_CONFIG, API_RETRY_ATTEMPTS, API_RETRY_MIN_WAIT, API_RETRY_MAX_WAIT


class EmbeddingGenerator:
    """Google Embedding APIを使用したEmbedding生成クラス"""

    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: Google AI Studio APIキー。Noneの場合は環境変数から取得
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Google API Keyが設定されていません。\n"
                "環境変数GOOGLE_API_KEYを設定するか、api_keyパラメータを使用してください"
            )

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_CONFIG["model"],
            google_api_key=self.api_key,
            task_type=EMBEDDING_CONFIG["task_type"]
        )

    @retry(
        stop=stop_after_attempt(API_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=API_RETRY_MIN_WAIT,
            max=API_RETRY_MAX_WAIT
        )
    )
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        複数のテキストのEmbeddingをドキュメント用に生成

        Args:
            texts: Embeddingを生成するテキストのリスト

        Returns:
            Embeddingベクトルのリスト
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"Embeddingエラー: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(API_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=API_RETRY_MIN_WAIT,
            max=API_RETRY_MAX_WAIT
        )
    )
    def embed_query(self, text: str) -> List[float]:
        """
        単一テキストのEmbeddingをクエリ用に生成

        Args:
            text: Embeddingを生成する単一テキスト

        Returns:
            Embeddingベクトル
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"クエリEmbeddingエラー: {str(e)}")
            raise

    def get_embedding_function(self):
        """
        LangChainのベクトルストアで使用するEmbedding関数を取得

        Returns:
            Embedding関数のインスタンス
        """
        return self.embeddings
