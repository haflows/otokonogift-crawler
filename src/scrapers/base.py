"""
スクレイパーの基底クラスモジュール
"""
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional
from dataclasses import dataclass

from config.settings import REQUEST_TIMEOUT, REQUEST_DELAY, USER_AGENT

logger = logging.getLogger(__name__)

@dataclass
class ArticleItem:
    """スクレイピングで取得した記事データ"""
    title: str
    url: str
    source_name: str
    content: str
    category_hint: str = "other"
    image_url: Optional[str] = None
    published_date: Optional[str] = None

class BaseScraper:
    """共通のスクレイピング機能を提供する基底クラス"""

    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request_time = 0.0

    def _wait_for_rate_limit(self):
        """礼儀正しいスクレイピングのための待機時間処理"""
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """URLのHTMLを取得し、BeautifulSoupオブジェクトを返す"""
        self._wait_for_rate_limit()
        try:
            logger.info(f"[{self.source_name}] ページ取得中: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self._last_request_time = time.time()
            return BeautifulSoup(response.content, "lxml")
        except Exception as e:
            logger.error(f"[{self.source_name}] ページ取得エラー ({url}): {e}")
            return None

    def fetch_text(self, url: str) -> Optional[str]:
        """URLからテキスト（RSSなど）を取得する"""
        self._wait_for_rate_limit()
        try:
            logger.info(f"[{self.source_name}] データ取得中: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self._last_request_time = time.time()
            return response.text
        except Exception as e:
            logger.error(f"[{self.source_name}] データ取得エラー ({url}): {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """不要な空白や改行を自動で除去するテキスト整形関数"""
        if not text:
            return ""
        return " ".join(text.split())

    def scrape(self) -> list[ArticleItem]:
        """各種スクレイパーで実装する個別の取得ロジック"""
        raise NotImplementedError("各スクレイパーでscrapeメソッドを実装してください")

    def run(self) -> list[ArticleItem]:
        """スクレイパーを実行し、記事リストを返す"""
        try:
            logger.info(f"=== {self.source_name} スクレイピング開始 ===")
            articles = self.scrape()
            if not articles:
                logger.warning(f"[{self.source_name}] 記事が1件も取得できませんでした")
                return []
            
            logger.info(f"[{self.source_name}] {len(articles)}件の記事を取得しました")
            return articles
        except Exception as e:
            logger.error(f"[{self.source_name}] スクレイピング中に予期せぬエラーが発生しました: {e}")
            return []
