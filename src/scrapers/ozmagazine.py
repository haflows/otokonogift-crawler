"""
OZmagazine スクレイパー
お出かけスポット・カフェ・イベント情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

TARGET_URLS = [
    ("https://www.ozmall.co.jp/ozmagazine/", "event"),
    ("https://www.ozmall.co.jp/restaurant/", "experience"),
    ("https://www.ozmall.co.jp/relaxation/", "experience"),
]


class OZMagazineScraper(BaseScraper):
    def __init__(self):
        super().__init__("OZmagazine", "https://www.ozmall.co.jp")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in TARGET_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            article_elems = soup.select(
                "article, div.article-card, div.feature-card, "
                "li.article-item, div.pickup-item, a.card-link"
            )

            if not article_elems:
                article_elems = soup.select("a[href*='ozmall.co.jp/']")

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
                        href = f"https://www.ozmall.co.jp{href}"

                    title = ""
                    title_tag = elem.find(["h2", "h3", "h4", "span"])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue

                    desc = ""
                    desc_tag = elem.find("p")
                    if desc_tag:
                        desc = desc_tag.get_text(strip=True)

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
                    logger.warning(f"[OZmagazine] 記事解析スキップ: {e}")

        return articles
