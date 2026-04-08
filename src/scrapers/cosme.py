"""
@cosme（アットコスメ）スクレイパー
コスメ・スキンケアの人気ランキング・新商品情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

TARGET_URLS = [
    ("https://www.cosme.net/bestcosme/", "cosmetics"),
    ("https://www.cosme.net/ranking/", "cosmetics"),
    ("https://www.cosme.net/feature/", "cosmetics"),
]


class CosmeScraper(BaseScraper):
    def __init__(self):
        super().__init__("@cosme", "https://www.cosme.net")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        for url, category in TARGET_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            # ランキングアイテムや特集記事を取得
            items = soup.select(
                "div.ranking-item, article, div.feature-card, "
                "li.product-item, div.cosme-product, a.card"
            )

            if not items:
                items = soup.select("a[href*='cosme.net/']")

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
                        href = f"https://www.cosme.net{href}"

                    title = ""
                    title_tag = item.find(["h2", "h3", "h4", "span.product-name"])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue

                    desc = ""
                    desc_tag = item.find("p")
                    if desc_tag:
                        desc = desc_tag.get_text(strip=True)

                    # 価格情報
                    price = ""
                    price_tag = item.find(string=lambda t: t and "円" in t)
                    if price_tag:
                        price = price_tag.strip()

                    img_url = None
                    img_tag = item.find("img")
                    if img_tag:
                        img_url = img_tag.get("src") or img_tag.get("data-src")

                    articles.append(ArticleItem(
                        title=title,
                        url=href,
                        source_name=self.source_name,
                        content=self._clean_text(f"{desc} {price}".strip() or title),
                        category_hint=category,
                        image_url=img_url,
                    ))
                except Exception as e:
                    logger.warning(f"[@cosme] 解析スキップ: {e}")

        return articles
