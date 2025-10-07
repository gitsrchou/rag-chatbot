"""
パフォーマンス計測ユーティリティ
処理時間の計測とレポート生成機能
"""

import time
from typing import Dict, List, Any
from contextlib import contextmanager


class PerformanceTracker:
    """パフォーマンス計測クラス"""

    def __init__(self):
        self.metrics = {}
        self.history = []

    @contextmanager
    def track(self, metric_name: str):
        """
        コンテキストマネージャーで処理時間を計測

        Args:
            metric_name: メトリクス名

        使用例:
            tracker = PerformanceTracker()
            with tracker.track("search"):
                # 処理
                pass
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            self.add_metric(metric_name, elapsed_time)

    def add_metric(self, name: str, value: float):
        """
        メトリクスを追加

        Args:
            name: メトリクス名
            value: 値（通常は秒単位の時間）
        """
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_average(self, name: str) -> float:
        """
        メトリクスの平均値を取得

        Args:
            name: メトリクス名

        Returns:
            平均値
        """
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        return sum(self.metrics[name]) / len(self.metrics[name])

    def get_total(self, name: str) -> float:
        """
        メトリクスの合計値を取得

        Args:
            name: メトリクス名

        Returns:
            合計値
        """
        if name not in self.metrics:
            return 0.0
        return sum(self.metrics[name])

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """
        全メトリクスのサマリーを取得

        Returns:
            メトリクス名をキーとする統計情報の辞書
        """
        summary = {}
        for name, values in self.metrics.items():
            if values:
                summary[name] = {
                    'count': len(values),
                    'total': sum(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        return summary

    def reset(self):
        """全メトリクスをリセット"""
        self.metrics = {}
        self.history = []

    def format_time(self, seconds: float) -> str:
        """
        秒数をバイト数から人間が読みやすい形式に変換

        Args:
            seconds: 秒数

        Returns:
            フォーマットされた時間文字列
        """
        if seconds < 0.001:
            return f"{seconds * 1000000:.2f} μs"
        elif seconds < 1:
            return f"{seconds * 1000:.2f} ms"
        else:
            return f"{seconds:.2f} s"


def compare_chunk_sizes(
    test_configs: List[Dict[str, Any]],
    test_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    複数のチャンクサイズのパフォーマンスを比較

    Args:
        test_configs: テスト設定のリスト
        test_results: テスト結果のリスト

    Returns:
        比較結果の辞書
    """
    comparison = {
        'configs': test_configs,
        'results': test_results,
        'best_config': None,
        'best_score': float('inf')
    }

    # 最も速い設定を見つける（総処理時間が最小のもの）
    for i, result in enumerate(test_results):
        total_time = result.get('performance', {}).get('total_time', float('inf'))
        if total_time < comparison['best_score']:
            comparison['best_score'] = total_time
            comparison['best_config'] = test_configs[i]

    return comparison


def format_performance_report(performance_data: Dict[str, Any]) -> str:
    """
    パフォーマンスデータを整形してレポート文字列を生成

    Args:
        performance_data: パフォーマンスデータ

    Returns:
        フォーマットされたレポート文字列
    """
    tracker = PerformanceTracker()

    report_lines = ["## パフォーマンスレポート\n"]

    if 'search_time' in performance_data:
        search_time_str = tracker.format_time(performance_data['search_time'])
        report_lines.append(f"- 検索時間: {search_time_str}")

    if 'generation_time' in performance_data:
        gen_time_str = tracker.format_time(performance_data['generation_time'])
        report_lines.append(f"- 回答生成時間: {gen_time_str}")

    if 'total_time' in performance_data:
        total_time_str = tracker.format_time(performance_data['total_time'])
        report_lines.append(f"- 総処理時間: {total_time_str}")

    if 'num_results' in performance_data:
        report_lines.append(f"- 検索結果数: {performance_data['num_results']}件")

    return "\n".join(report_lines)
