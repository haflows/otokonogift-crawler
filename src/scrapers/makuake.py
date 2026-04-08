"""
Makuake スクレイパー
クラウドファンディングのユニークなギフト候補を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

# 女性向けギフトに関連するカテゴリ
TARGET_URLS = [
    ("https://www.makuake.com/discover/?category=fashion_beauty", "fashion"),
    ("https://www.makuake.com/discover/?category=food_drink", "sweets"),
    ("https://www.makuake.com/discover/?category=interior_daily", "new_product"),
]


class MakuakeScraper(BaseScraper):
    def __init__(self):
        super().__init__("Makuake", "https://www.makuake.com")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in TARGET_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            items = soup.select(
                "div.project-card, article, div.card, "
                "li.project-item, a.project-link"
            )

            if not items:
                items = soup.select("a[href*='makuake.com/project/']")

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
                        href = f"https://www.makuake.com{href}"

                    title = ""
                    title_tag = item.find(["h2", "h3", "h4", "p.project-title"])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    desc = ""
                    desc_tag = item.find("p")
                    if desc_tag and desc_tag != title_tag:
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
                    logger.warning(f"[Makuake] 解析スキップ: {e}")

        return articles
