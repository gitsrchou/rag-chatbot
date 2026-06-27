# src/loader.py
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)


class DocumentLoader:
    def __init__(self, directory: str):
        self.directory = directory

    def load_documents(self) -> List[Document]:
        """指定ディレクトリ以下のすべての文書を読み込む"""
        all_docs = []

        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)

                try:
                    docs = self.load_file(file_path)
                    all_docs.extend(docs)
                except Exception as e:
                    print(f"読み込み失敗: {file_path}, エラー: {e}")

        return all_docs

    def load_file(self, file_path: str) -> List[Document]:
        """拡張子に応じて適切なローダーで読み込む"""

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)

        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)

        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")

        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)

        else:
            raise ValueError(f"未対応のファイル形式: {file_path}")

        docs = loader.load()

        # metadata に source を追加
        for d in docs:
            d.metadata["source"] = file_path

        return docs
