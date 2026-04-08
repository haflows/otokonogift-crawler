"""
sweet web スクレイパー
ファッション・コスメ・美容トレンド情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

CATEGORY_URLS = [
    ("https://sweetweb.jp/category/beauty/", "cosmetics"),
    ("https://sweetweb.jp/category/fashion/", "fashion"),
    ("https://sweetweb.jp/category/lifestyle/", "other"),
]


class SweetScraper(BaseScraper):
    def __init__(self):
        super().__init__("sweet web", "https://sweetweb.jp")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in CATEGORY_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            article_elems = soup.select("article, div.post-card, div.entry-card, li.post-item")

            if not article_elems:
                article_elems = soup.select("a[href*='sweetweb.jp/']")

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
                        href = f"https://sweetweb.jp{href}"

                    title = ""
                    title_tag = elem.find(["h2", "h3", "h4"])
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
                    logger.warning(f"[sweet] 記事解析スキップ: {e}")

        return articles
