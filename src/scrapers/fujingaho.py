"""
婦人画報 スクレイパー
上質なライフスタイル・グルメ・ギフト情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

TARGET_URLS = [
    ("https://www.fujingaho.jp/lifestyle/gift/", "new_product"),
    ("https://www.fujingaho.jp/gourmet/", "sweets"),
    ("https://www.fujingaho.jp/beauty/", "cosmetics"),
]


class FujingahoScraper(BaseScraper):
    def __init__(self):
        super().__init__("婦人画報", "https://www.fujingaho.jp")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in TARGET_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            items = soup.select(
                "article, div.article-card, div.content-card, "
                "li.article-item, a.article-link"
            )

            if not items:
                items = soup.select("a[href*='fujingaho.jp/']")

            for item in items[:10]:
                try:
                    if item.name == "a":
                        link_tag = item
                    else:
                        link_tag = item.find("a")

                    if not link_tag:
                        continue

                    href = link_tag.get("href", "")
                    if not href:
                        continue
                    if href.startswith("/"):
                        href = f"https://www.fujingaho.jp{href}"

                    title = ""
                    title_tag = item.find(["h2", "h3", "h4"])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    desc = ""
                    desc_tag = item.find("p")
                    if desc_tag:
                        desc = desc_tag.get_text(strip=True)

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
                    logger.warning(f"[婦人画報] 解析スキップ: {e}")

        return articles
