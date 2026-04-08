"""
PR TIMES スクレイパー
企業の公式プレスリリースから新商品・イベント情報を取得
"""
import feedparser
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

# ギフト関連のキーワードでフィルタリングするRSSカテゴリ
RSS_FEEDS = [
    # ファッション・ビューティー
    "https://prtimes.jp/rss/cat/fashion.rdf",
    # グルメ
    "https://prtimes.jp/rss/cat/food.rdf",
    # ライフスタイル
    "https://prtimes.jp/rss/cat/life.rdf",
]

# プレスリリースのタイトルに含まれるべきキーワード（いずれか）
KEYWORDS = [
    "ギフト", "プレゼント", "限定", "コラボ", "新作", "新発売",
    "バレンタイン", "ホワイトデー", "クリスマス", "母の日",
    "誕生日", "記念日", "アニバーサリー",
    "スイーツ", "チョコレート", "ケーキ", "和菓子",
    "コスメ", "香水", "美容", "スキンケア",
    "ジュエリー", "アクセサリー", "ネックレス", "リング",
    "花", "フラワー", "ブーケ",
    "体験", "スパ", "エステ", "アフタヌーンティー",
    "ポップアップ", "期間限定", "数量限定",
    "ブランド", "高級", "プレミアム",
    "イベント", "フェア", "展覧会", "展示",
]


class PRTimesScraper(BaseScraper):
    def __init__(self):
        super().__init__("PR TIMES", "https://prtimes.jp")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for feed_url in RSS_FEEDS:
            try:
                text = self.fetch_text(feed_url)
                if not text:
                    continue

                feed = feedparser.parse(text)
                for entry in feed.entries:
                    title = entry.get("title", "")
                    # キーワードフィルタリング
                    if not any(kw in title for kw in KEYWORDS):
                        continue

                    summary = entry.get("summary", "")
                    link = entry.get("link", "")
                    published = entry.get("published", "")

                    articles.append(ArticleItem(
                        title=title,
                        url=link,
                        source_name=self.source_name,
                        content=self._clean_text(summary),
                        category_hint="new_product",
                        published_date=published,
                    ))
            except Exception as e:
                logger.error(f"[PR TIMES] RSS解析エラー ({feed_url}): {e}")

        return articles
