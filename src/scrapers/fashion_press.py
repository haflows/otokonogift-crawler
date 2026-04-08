"""
FASHION PRESS スクレイパー
ファッション・ビューティー・スイーツの新着ニュースを取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

# 取得対象のカテゴリページ
CATEGORY_URLS = [
    ("https://www.fashion-press.net/news/beauty", "cosmetics"),
    ("https://www.fashion-press.net/news/gourmet", "sweets"),
    ("https://www.fashion-press.net/news/fashion", "fashion"),
    ("https://www.fashion-press.net/news/event", "event"),
]


class FashionPressScraper(BaseScraper):
    def __init__(self):
        super().__init__("FASHION PRESS", "https://www.fashion-press.net")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in CATEGORY_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            # FASHION PRESSのニュース記事リスト
            # 記事カードを取得（CSSセレクタはサイト構造に依存）
            news_items = soup.select("article.news-item, div.news-card, li.news-list-item")

            if not news_items:
                # フォールバック: a タグからニュース記事を探す
                news_items = soup.select("a[href*='/news/']")

            for item in news_items[:10]:
                try:
                    # タイトルとURLの取得
                    if item.name == "a":
                        link_tag = item
                    else:
                        link_tag = item.find("a")

                    if not link_tag:
                        continue

                    href = link_tag.get("href", "")
                    if not href or "/news/" not in href:
                        continue

                    # 完全なURLに変換
                    if href.startswith("/"):
                        href = f"https://www.fashion-press.net{href}"

                    title = link_tag.get_text(strip=True)
                    if not title or len(title) < 5:
                        # タイトルが短すぎる場合、親要素から取得を試みる
                        title_tag = item.find(["h2", "h3", "p"])
                        if title_tag:
                            title = title_tag.get_text(strip=True)

                    if not title or len(title) < 5:
                        continue

                    # 説明文の取得
                    desc = ""
                    desc_tag = item.find(["p", "span"], class_=lambda c: c and ("desc" in str(c).lower() or "text" in str(c).lower()))
                    if desc_tag:
                        desc = desc_tag.get_text(strip=True)

                    # 画像の取得
                    img_url = None
                    img_tag = item.find("img")
                    if img_tag:
                        img_url = img_tag.get("src") or img_tag.get("data-src")

                    articles.append(ArticleItem(
                        title=title,
                        url=href,
                        source_name=self.source_name,
                        content=self._clean_text(desc or title),
                        category_hint=category,
                        image_url=img_url,
                    ))
                except Exception as e:
                    logger.warning(f"[FASHION PRESS] 記事解析スキップ: {e}")

        return articles
