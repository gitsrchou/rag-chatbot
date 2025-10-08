"""
QAチェーンモジュール
LangChainとGeminiを使用した質問応答システム
"""

import os
import time
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
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
    """質問応答チェーンクラス"""

    def __init__(
        self,
        retriever: Retriever,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_output_tokens: int = None
    ):
        """
        Args:
            retriever: Retrieverのインスタンス
            api_key: Google AI Studio APIキー
            model: 使用するモデル名
            temperature: 温度パラメータ
            max_output_tokens: 最大出力トークン数
        """
        self.retriever = retriever
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError("Google API Keyが設定されていません")

        # LLM設定
        self.model = model or LLM_CONFIG["model"]["default"]
        self.temperature = temperature if temperature is not None else LLM_CONFIG["temperature"]["default"]
        self.max_output_tokens = max_output_tokens or LLM_CONFIG["max_output_tokens"]["default"]

        # LLMの初期化
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens
        )

        # プロンプトテンプレートの設定
        self.prompt_template = PromptTemplate(
            template=QA_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )

        # チェーンの作成
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template
        )

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
        """
        質問に対して回答を生成

        Args:
            question: 質問文
            top_k: 検索で取得するドキュメント数
            score_threshold: 類似度スコアの閾値

        Returns:
            回答と検索結果を含む辞書
        """
        try:
            # 1. 関連ドキュメントを検索
            search_start = time.time()
            search_results = self.retriever.search(
                query=question,
                top_k=top_k,
                score_threshold=score_threshold,
                return_scores=True
            )
            search_time = time.time() - search_start

            documents = search_results['documents']

            if not documents:
                return {
                    'answer': '関連する情報が見つかりませんでした。この質問には答えられません',
                    'sources': [],
                    'performance': {
                        'search_time': search_time,
                        'generation_time': 0.0,
                        'total_time': search_time
                    }
                }

            # 2. コンテキストを生成
            context = self.retriever.get_context_for_llm(documents)

            # 3. LLMで回答を生成
            generation_start = time.time()
            response = self.chain.invoke({
                'context': context,
                'question': question
            })
            generation_time = time.time() - generation_start

            # 4. 結果を整形
            formatted_sources = self.retriever.format_results(search_results)

            total_time = search_time + generation_time

            return {
                'answer': response['text'],
                'sources': formatted_sources,
                'performance': {
                    'search_time': search_time,
                    'generation_time': generation_time,
                    'total_time': total_time
                }
            }

        except Exception as e:
            raise Exception(f"回答生成エラー: {str(e)}")

    def answer_question_stream(self, question: str, top_k: int = None, score_threshold: float = None):
        """
        質問に対してストリーミングで回答を生成

        Args:
            question: 質問文
            top_k: 検索で取得するドキュメント数
            score_threshold: 類似度スコアの閾値

        Yields:
            回答のチャンク
        """
        # 検索
        search_results = self.retriever.search(
            query=question,
            top_k=top_k,
            score_threshold=score_threshold,
            return_scores=True
        )

        documents = search_results['documents']

        if not documents:
            yield '関連する情報が見つかりませんでした。この質問には答えられません'
            return

        # コンテキスト生成
        context = self.retriever.get_context_for_llm(documents)

        # プロンプト生成
        prompt = self.prompt_template.format(context=context, question=question)

        for chunk in self.llm.stream(prompt):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)

    def update_config(
        self,
        model: str = None,
        temperature: float = None,
        max_output_tokens: int = None
    ):
        """
        LLM設定を更新

        Args:
            model: モデル名
            temperature: 温度パラメータ
            max_output_tokens: 最大出力トークン数
        """
        if model:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_output_tokens:
            self.max_output_tokens = max_output_tokens

        # LLMを再初期化
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens
        )

        # チェーンを再作成
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template
        )
