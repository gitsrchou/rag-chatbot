# ingest.py
import os
from src.loader import DocumentLoader
from src.vector_store import VectorStore
from src.embeddings import EmbeddingGenerator

DATA_DIR = "./data"  # 文書フォルダ
CHROMA_DIR = "./chroma"  # ベクトルDB保存先

def main():
    print("=== 文書の読み込みを開始します ===")

    # 1. 文書ロード
    loader = DocumentLoader(DATA_DIR)
    documents = loader.load_documents()
    print(f"読み込んだ文書数: {len(documents)}")

    # 2. Embedding モデルの準備
    embedder = EmbeddingGenerator(model="nomic-embed-text")

    # 3. ベクトルストア作成
    vector_store = VectorStore(
        persist_directory=CHROMA_DIR,
        embedding_function=embedder
    )

    # 4. 文書を追加して保存
    print("=== ベクトルDBへ文書を追加します ===")
    vector_store.add_documents(documents)
    vector_store.persist()

    print("=== インデックス作成完了 ===")

if __name__ == "__main__":
    main()
