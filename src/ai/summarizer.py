"""
Gemini API を使った記事の要約・フィルタリング・スコアリング
"""
import json
import logging
import time
from typing import Optional
from dataclasses import dataclass

from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SYSTEM_PROMPT,
    ANALYSIS_PROMPT_TEMPLATE,
    CATEGORIES,
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """AI分析結果"""
    is_relevant: bool
    gift_score: int  # 1-5
    category: str  # カテゴリキー
    category_label: str  # カテゴリ表示名（絵文字付き）
    summary: str
    post_idea: str
    estimated_price: Optional[str]


class ArticleSummarizer:
    """Gemini APIを使って記事を分析・要約する"""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY が設定されていません。.envファイルを確認してください。")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def analyze_article(self, title: str, url: str, content: str, source_name: str) -> Optional[AnalysisResult]:
        """
        1つの記事を分析し、ギフト適合度などを判定する
        """
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            source_name=source_name,
            title=title,
            url=url,
            content=content[:800],  # トークン節約のため800文字に制限
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,  # 低めのtemperatureで安定した出力を得る
                    response_mime_type="application/json",
                ),
            )

            # レスポンスからJSONを抽出
            result_text = response.text.strip()

            # JSON解析
            try:
                data = json.loads(result_text)
            except json.JSONDecodeError:
                # JSONブロック内にある場合の処理
                if "```json" in result_text:
                    json_str = result_text.split("```json")[1].split("```")[0].strip()
                    data = json.loads(json_str)
                elif "```" in result_text:
                    json_str = result_text.split("```")[1].split("```")[0].strip()
                    data = json.loads(json_str)
                else:
                    logger.warning(f"JSON解析失敗: {result_text[:200]}")
                    return None

            is_relevant = data.get("is_relevant", False)
            if not is_relevant:
                return AnalysisResult(
                    is_relevant=False,
                    gift_score=0,
                    category="other",
                    category_label=CATEGORIES.get("other", "📌その他"),
                    summary="",
                    post_idea="",
                    estimated_price=None,
                )

            category_key = data.get("category", "other")
            return AnalysisResult(
                is_relevant=True,
                gift_score=int(data.get("gift_score", 3)),
                category=category_key,
                category_label=CATEGORIES.get(category_key, CATEGORIES["other"]),
                summary=data.get("summary", ""),
                post_idea=data.get("post_idea", ""),
                estimated_price=data.get("estimated_price"),
            )

        except Exception as e:
            logger.error(f"Gemini API エラー: {e}")
            return None

    def analyze_batch(self, articles: list) -> list[tuple]:
        """
        複数の記事をバッチ分析する
        Returns: list of (article, analysis_result) tuples
        """
        results = []
        total = len(articles)

        for i, article in enumerate(articles, 1):
            logger.info(f"[AI分析] {i}/{total}: {article.title[:50]}...")

            result = self.analyze_article(
                title=article.title,
                url=article.url,
                content=article.content,
                source_name=article.source_name,
            )

            if result and result.is_relevant and result.gift_score >= 3:
                results.append((article, result))
                logger.info(f"  → ✅ 採用 (スコア: {result.gift_score}, カテゴリ: {result.category_label})")
            elif result and result.is_relevant:
                logger.info(f"  → ⚠️ スコア低 (スコア: {result.gift_score}) - スキップ")
            else:
                logger.info(f"  → ❌ 不適切 - スキップ")

            # レートリミット対策（無料枠は15 RPM）
            time.sleep(4)

        logger.info(f"[AI分析] 完了: {len(results)}/{total}件 を採用")
        return results
