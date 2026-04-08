"""
三越伊勢丹オンライン スクレイパー
新商品・限定品・ギフト特集情報を取得
"""
import logging
from .base import BaseScraper, ArticleItem

logger = logging.getLogger(__name__)

TARGET_URLS = [
    ("https://www.mistore.jp/shopping/feature/foods_f2/sweets_lucky_bag", "limited"),
    ("https://www.mistore.jp/shopping/feature/foods_f2/gift_ranking", "new_product"),
    ("https://www.mistore.jp/shopping/feature/beauty_f1/cosme_gift", "cosmetics"),
]


class MistoreScraper(BaseScraper):
    def __init__(self):
        super().__init__("三越伊勢丹", "https://www.mistore.jp")

    def scrape(self) -> list[ArticleItem]:
        articles = []

        # まずトップページ・ギフト特集を確認
        main_url = "https://www.mistore.jp/shopping"
        soup = self.fetch_page(main_url)

        if soup:
            # 特集・キャンペーンバナーを取得
            banners = soup.select(
                "a[href*='feature'], a[href*='gift'], "
                "div.banner a, div.feature a, div.campaign a"
            )

            for banner in banners[:15]:
                try:
                    href = banner.get("href", "")
                    if not href:
                        continue
                    if href.startswith("/"):
                        href = f"https://www.mistore.jp{href}"

                    title = banner.get_text(strip=True)
                    if not title:
                        img = banner.find("img")
                        if img:
                            title = img.get("alt", "")
                    if not title or len(title) < 3:
                        continue

                    # ギフト関連のキーワードでフィルタ
                    gift_keywords = [
                        "ギフト", "限定", "プレゼント", "特集", "コラボ",
                        "新作", "スイーツ", "コスメ", "ビューティー",
                        "母の日", "クリスマス", "バレンタイン", "ホワイトデー",
                    ]
                    if not any(kw in title for kw in gift_keywords):
                        continue

                    img_url = None
                    img_tag = banner.find("img")
                    if img_tag:
                        img_url = img_tag.get("src") or img_tag.get("data-src")

                    articles.append(ArticleItem(
                        title=title,
                        url=href,
                        source_name=self.source_name,
                        content=self._clean_text(title),
                        category_hint="new_product",
                        image_url=img_url,
                    ))
                except Exception as e:
                    logger.warning(f"[三越伊勢丹] 解析スキップ: {e}")

        # 追加の特集ページもチェック
        for url, category in TARGET_URLS:
            soup = self.fetch_page(url)
            if not soup:
                continue

            items = soup.select("div.product-item, div.item-card, article, li.item")
            for item in items[:5]:
                try:
                    link_tag = item.find("a")
                    if not link_tag:
                        continue
                    href = link_tag.get("href", "")
                    if href.startswith("/"):
                        href = f"https://www.mistore.jp{href}"

                    title = ""
                    title_tag = item.find(["h2", "h3", "p"])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    if not title:
                        title = link_tag.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue

                    articles.append(ArticleItem(
                        title=title,
                        url=href,
                        source_name=self.source_name,
                        content=self._clean_text(title),
                        category_hint=category,
                    ))
                except Exception as e:
                    logger.warning(f"[三越伊勢丹] 商品解析スキップ: {e}")

        return articles
