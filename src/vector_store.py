"""
ベクトルDBモジュール
Cloud / Local 切り替え対応版
Cloud → FAISS（永続化なし）
Local → Chroma（永続化あり）
"""

import os
from typing import List, Optional
from langchain_core.documents import Document
from config.settings import CHROMA_DB_PATH, COLLECTION_NAME

# Cloud / Local 判定
IS_CLOUD = os.getenv("ENV") == "cloud"

# Cloud → FAISS（永続化不要）
# Local → Chroma（永続化あり）
if IS_CLOUD:
    from langchain_community.vectorstores import FAISS
else:
    from langchain_chroma import Chroma


class VectorStore:
    """Cloud / Local 切替対応ベクトルストア管理クラス"""

    def __init__(self, embedding_function, persist_directory: str = None, collection_name: str = None):
        self.embedding_function = embedding_function
        self.persist_directory = persist_directory or CHROMA_DB_PATH
        self.collection_name = collection_name or COLLECTION_NAME
        self.vector_store = None

        # Local のみ永続化ディレクトリを作成
        if not IS_CLOUD:
            os.makedirs(self.persist_directory, exist_ok=True)

    def create_from_documents(self, documents: List[Document]) -> None:
        """
        ドキュメントからベクトルストアを作成
        Cloud → FAISS（メモリ）
        Local → Chroma（永続化）
        """
        if IS_CLOUD:
            self.vector_store = FAISS.from_documents(
                documents,
                self.embedding_function
            )
        else:
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )

    def load_existing(self) -> bool:
        """
        既存のベクトルストアを読み込む
        Cloud → 永続化不可なので False
        Local → Chroma の永続化ディレクトリを読み込む
        """
        if IS_CLOUD:
            return False

        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
                collection_name=self.collection_name
            )
            count = self.vector_store._collection.count()
            return count > 0
        except Exception:
            return False

    def add_documents(self, documents: List[Document]) -> None:
        """既存のベクトルストアにドキュメントを追加"""
        if self.vector_store is None:
            raise ValueError("ベクトルストアが初期化されていません")

        self.vector_store.add_documents(documents)

        # Local のみ永続化
        if not IS_CLOUD:
            self.vector_store.persist()

    def similarity_search(self, query: str, k: int = 5, score_threshold: Optional[float] = None):
        """類似度検索（Cloud / Local 共通）"""
        if self.vector_store is None:
            raise ValueError("ベクトルストアが初期化されていません")

        if score_threshold is not None:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            filtered = [doc for doc, score in results if score >= score_threshold]
            return filtered
        else:
            return self.vector_store.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 5):
        """スコア付き類似度検索"""
        if self.vector_store is None:
            raise ValueError("ベクトルストアが初期化されていません")

        return self.vector_store.similarity_search_with_score(query, k=k)

    def delete_collection(self) -> None:
        """コレクションを削除"""
        if self.vector_store is not None and not IS_CLOUD:
            self.vector_store.delete_collection()
        self.vector_store = None

    def get_vector_store(self):
        """ベクトルストアのインスタンスを取得"""
        return self.vector_store

    def get_document_count(self) -> int:
        """ベクトルストア内のドキュメント数を取得"""
        if self.vector_store is None:
            return 0

        try:
            if IS_CLOUD:
                # FAISS は index_to_docstore_id を持つ
                return len(self.vector_store.index_to_docstore_id)
            else:
                return self.vector_store._collection.count()
        except Exception:
            return 0
