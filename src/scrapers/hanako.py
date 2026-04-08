"""
Hanako Web スクレイパー
スイーツ・カフェ・お出かけスポット・トレンド情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

CATEGORY_URLS = [
    ("https://hanako.tokyo/category/food/", "sweets"),
    ("https://hanako.tokyo/category/travel/", "experience"),
    ("https://hanako.tokyo/category/lifestyle/", "other"),
]


class HanakoScraper(BaseScraper):
    def __init__(self):
        super().__init__("Hanako Web", "https://hanako.tokyo")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in CATEGORY_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            # Hanako Webの記事リスト取得
            article_elems = soup.select("article, div.post-item, div.article-card, li.article-list__item")

            if not article_elems:
                # フォールバック: 記事リンクを直接探す
                article_elems = soup.select("a[href*='hanako.tokyo/']")

            for elem in article_elems[:10]:
                try:
                    if elem.name == "a":
                        link_tag = elem
                    else:
                        link_tag = elem.find("a")

                    if not link_tag:
                        continue

                    href = link_tag.get("href", "")
                    if not href:
                        continue
                    if href.startswith("/"):
                        href = f"https://hanako.tokyo{href}"

                    # タイトル取得
                    title = ""
                    title_tag = elem.find(["h2", "h3", "h4"])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    # 説明文
                    desc = ""
                    desc_tag = elem.find("p")
                    if desc_tag:
                        desc = desc_tag.get_text(strip=True)

                    # 画像
                    img_url = None
                    img_tag = elem.find("img")
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
                    logger.warning(f"[Hanako] 記事解析スキップ: {e}")

        return articles
