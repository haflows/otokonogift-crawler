"""
一休.com スクレイパー
高級レストラン・スパ・ホテル体験の新着・特集情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

TARGET_URLS = [
    ("https://www.ikyu.com/concierge/", "experience"),
    ("https://restaurant.ikyu.com/area/tokyo/", "experience"),
]


class IkyuScraper(BaseScraper):
    def __init__(self):
        super().__init__("一休.com", "https://www.ikyu.com")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in TARGET_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            # コンシェルジュ記事・特集記事
            items = soup.select(
                "article, div.article-card, div.concierge-card, "
                "li.feature-item, a.article-link, div.pickup"
            )

            if not items:
                items = soup.select("a[href*='ikyu.com/']")

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
                        href = f"https://www.ikyu.com{href}"

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
                    logger.warning(f"[一休.com] 解析スキップ: {e}")

        return articles
