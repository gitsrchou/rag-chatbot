# test_loader.py
from src.document_loader import DocumentLoader
from langchain_core.documents import Document

loader = DocumentLoader()

# ディレクトリから読み込み
documents = loader.load_directory('./data/raw')

print(f"読み込んだドキュメントページ数: {len(documents)}")
# ファイルごとに最初の1ページだけ表示
seen_files = set()

for doc in documents:
    source = doc.metadata.get("source")

    if source not in seen_files:
        seen_files.add(source)

        print(f"\n--- ファイル: {source} ---")
        print(f"テキスト（最初の100文字）: {doc.page_content[:100]}...")

#for i, doc in enumerate(documents[:len(documents)]):
#    print(f"\n--- ドキュメント {i+1} ---")
#    print(f"ソース: {doc.metadata.get('source', 'Unknown')}")
#    print(f"テキスト（最初の100文字）: {doc.page_content[:100]}...")
