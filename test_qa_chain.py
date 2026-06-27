# test_qa_chain.py
import os
from dotenv import load_dotenv

from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.qa_chain import QAChain

load_dotenv()

# === Embedding モデル（Ollama） ===
# 例: snowflake-arctic-embed / nomic-embed-text / mxbai-embed-large
embedding_gen = EmbeddingGenerator(model="snowflake-arctic-embed")
#embedding_function = embedding_gen.get_embedding_function()
embedding_function = embedding_gen


# === 既存の ChromaDB を読み込み ===
vector_store = VectorStore(
    embedding_function=embedding_function,
    persist_directory="./chroma_db"
)

if not vector_store.load_existing():
    print("エラー: インデックスが見つかりません。先に ingest.py を実行してください。")
    exit(1)

# === Retriever 初期化 ===
retriever = Retriever(vector_store)

# === QAChain（Ollama LLM）初期化 ===
# 例: llama3, qwen2.5, phi3, mistral など
qa_chain = QAChain(
    retriever=retriever,
    model="llama3",
    temperature=0.2
)

# === 質問 ===
question = "有給休暇を取得するにはどうすればいいですか？"
print(f"質問: {question}\n")

# === 回答生成 ===
result = qa_chain.answer_question(question, top_k=3)

print("=== 回答 ===")
print(result["answer"])

print("\n=== 参照元 ===")
for source in result["sources"]:
    print(f"\n[{source['rank']}] {source['metadata'].get('source')} (スコア: {source['score']:.4f})")
    print(f"{source['content'][:150]}...")

print("\n=== パフォーマンス ===")
print(f"検索時間: {result['performance']['search_time']:.3f}秒")
print(f"生成時間: {result['performance']['generation_time']:.3f}秒")
print(f"総処理時間: {result['performance']['total_time']:.3f}秒")
