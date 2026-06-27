"""
QAチェーンモジュール（Ollama版）
LangChain + Ollama を使用した質問応答システム（Runnable版）
"""

import time
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

from tenacity import retry, stop_after_attempt, wait_exponential

from src.retriever import Retriever
from config.settings import (
    LLM_CONFIG,
    QA_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    API_RETRY_ATTEMPTS,
    API_RETRY_MIN_WAIT,
    API_RETRY_MAX_WAIT
)


class QAChain:
    """Ollama を使った質問応答チェーン（Runnable版）"""

    def __init__(
        self,
        retriever: Retriever,
        model: str = None,
        temperature: float = None,
        max_output_tokens: int = None
    ):
        self.retriever = retriever

        # LLM設定
        self.model = model or LLM_CONFIG["model"]["default"]
        self.temperature = temperature if temperature is not None else LLM_CONFIG["temperature"]["default"]
        self.max_output_tokens = max_output_tokens or LLM_CONFIG["max_output_tokens"]["default"]

        # Ollama LLM
        self.llm = ChatOllama(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_output_tokens,
            stream=False   # ← これが絶対必要
        )

        # プロンプト
        self.prompt = PromptTemplate(
            template=QA_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )

        # Runnable チェーン
        self.chain = RunnableSequence(self.prompt | self.llm)

    def update_config(
        self,
        model: str = None,
        temperature: float = None,
        max_output_tokens: int = None
    ):
        """LLM設定を更新（Ollama版）"""

        if model:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_output_tokens:
            self.max_output_tokens = max_output_tokens

        # Ollama LLM を再初期化
        self.llm = ChatOllama(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_output_tokens,
            stream=False   # ← これが絶対必要
        )

        # Runnable チェーンを再構築
        self.chain = self.prompt | self.llm





    @retry(
        stop=stop_after_attempt(API_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=API_RETRY_MIN_WAIT,
            max=API_RETRY_MAX_WAIT
        )
    )
    def answer_question(
        self,
        question: str,
        top_k: int = None,
        score_threshold: float = None
    ) -> Dict[str, Any]:

        try:
            # 1. RAG 検索
            search_start = time.time()
            search_results = self.retriever.search(
                query=question,
                top_k=top_k,
                score_threshold=score_threshold,
                return_scores=True
            )
            search_time = time.time() - search_start

            documents = search_results["documents"]

            if not documents:
                return {
                    "answer": "関連する情報が見つかりませんでした。",
                    "sources": [],
                    "performance": {
                        "search_time": search_time,
                        "generation_time": 0.0,
                        "total_time": search_time
                    }
                }

            # 2. コンテキスト生成
            context = self.retriever.get_context_for_llm(documents)

            # 3. LLM で回答生成
            generation_start = time.time()
            response = self.chain.invoke({
                "context": context,
                "question": question
            })
            # 安全に content を取り出す
            if hasattr(response, "content"):
                answer_text = response.content
            else:
                answer_text = str(response) 
            generation_time = time.time() - generation_start

            # 4. 検索結果整形
            formatted_sources = self.retriever.format_results(search_results)

            total_time = search_time + generation_time

            return {
                "answer": answer_text,
                "sources": formatted_sources,
                "performance": {
                    "search_time": search_time,
                    "generation_time": generation_time,
                    "total_time": total_time
                }
            }

        except Exception as e:
            raise Exception(f"回答生成エラー: {str(e)}")
