"""
Googleトレンド スクレイパー
ギフト関連のトレンドワードを取得
"""
import logging
from datetime import datetime

from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

# 監視するキーワード
TREND_KEYWORDS = [
    "プレゼント 女性",
    "ギフト 彼女",
    "限定 スイーツ",
    "コスメ 新作",
    "アフタヌーンティー",
    "体験 ギフト",
    "ポップアップ",
    "コラボ 限定",
]


class GoogleTrendsScraper(BaseScraper):
    def __init__(self):
        super().__init__("Googleトレンド", "https://trends.google.co.jp")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl="ja-JP", tz=540)

            # 各キーワードのトレンドを確認
            for keyword in TREND_KEYWORDS:
                try:
                    pytrends.build_payload([keyword], timeframe="now 7-d", geo="JP")
                    interest = pytrends.interest_over_time()

                    if interest.empty:
                        continue

                    # 直近のトレンド値
                    latest_value = int(interest[keyword].iloc[-1])

                    # トレンド値が一定以上の場合のみ記録
                    if latest_value >= 30:
                        # 関連クエリも取得
                        related = pytrends.related_queries()
                        related_terms = []
                        if keyword in related:
                            top_queries = related[keyword].get("top")
                            if top_queries is not None and not top_queries.empty:
                                related_terms = top_queries["query"].tolist()[:5]

                        articles.append(ArticleItem(
                            title=f"[トレンド] 「{keyword}」の検索が上昇中 (スコア: {latest_value})",
                            url=f"https://trends.google.co.jp/trends/explore?q={keyword}&geo=JP&date=now%207-d",
                            source_name=self.source_name,
                            content=f"「{keyword}」がGoogleトレンドでスコア{latest_value}を記録。"
                                    f"関連ワード: {', '.join(related_terms) if related_terms else 'なし'}",
                            category_hint="other",
                            published_date=datetime.now().isoformat(),
                        ))
                except Exception as e:
                    logger.warning(f"[Googleトレンド] キーワード「{keyword}」の取得失敗: {e}")
                    continue

        except ImportError:
            logger.warning("[Googleトレンド] pytrends がインストールされていません。スキップします。")
        except Exception as e:
            logger.error(f"[Googleトレンド] エラー: {e}")

        return articles
