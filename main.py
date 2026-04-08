"""
otokonogift ネタ探し自動化 - メインスクリプト

毎日定時に実行され、以下のフローを処理する：
1. 各情報源からスクレイピング
2. Gemini APIで要約・フィルタリング
3. Google Sheetsに結果を書き込み
"""
import sys
import logging
from datetime import datetime

from config.settings import SOURCES

# ──────────────────────────────────────────────
# ロギング設定
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def get_scrapers():
    """有効なスクレイパーのリストを取得"""
    scrapers = []

    if SOURCES.get("prtimes", {}).get("enabled"):
        from src.scrapers.prtimes import PRTimesScraper
        scrapers.append(PRTimesScraper())

    if SOURCES.get("fashion_press", {}).get("enabled"):
        from src.scrapers.fashion_press import FashionPressScraper
        scrapers.append(FashionPressScraper())

    if SOURCES.get("hanako", {}).get("enabled"):
        from src.scrapers.hanako import HanakoScraper
        scrapers.append(HanakoScraper())

    if SOURCES.get("sweet", {}).get("enabled"):
        from src.scrapers.sweet import SweetScraper
        scrapers.append(SweetScraper())

    if SOURCES.get("ozmagazine", {}).get("enabled"):
        from src.scrapers.ozmagazine import OZMagazineScraper
        scrapers.append(OZMagazineScraper())

    if SOURCES.get("mistore", {}).get("enabled"):
        from src.scrapers.mistore import MistoreScraper
        scrapers.append(MistoreScraper())

    if SOURCES.get("cosme", {}).get("enabled"):
        from src.scrapers.cosme import CosmeScraper
        scrapers.append(CosmeScraper())

    if SOURCES.get("ikyu", {}).get("enabled"):
        from src.scrapers.ikyu import IkyuScraper
        scrapers.append(IkyuScraper())

    if SOURCES.get("anny", {}).get("enabled"):
        from src.scrapers.anny import AnnyScraper
        scrapers.append(AnnyScraper())

    if SOURCES.get("fujingaho", {}).get("enabled"):
        from src.scrapers.fujingaho import FujingahoScraper
        scrapers.append(FujingahoScraper())

    if SOURCES.get("makuake", {}).get("enabled"):
        from src.scrapers.makuake import MakuakeScraper
        scrapers.append(MakuakeScraper())

    if SOURCES.get("google_trends", {}).get("enabled"):
        from src.scrapers.google_trends import GoogleTrendsScraper
        scrapers.append(GoogleTrendsScraper())

    return scrapers


def main():
    """メイン処理"""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("🎁 otokonogift ネタ探し自動化 開始")
    logger.info(f"📅 実行日時: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # ──────────────────────────────────────
    # Step 1: スクレイピング
    # ──────────────────────────────────────
    logger.info("\n📡 Step 1: 情報収集開始...")
    scrapers = get_scrapers()
    logger.info(f"  有効なスクレイパー: {len(scrapers)}個")

    all_articles = []
    for scraper in scrapers:
        articles = scraper.run()
        all_articles.extend(articles)

    logger.info(f"\n📊 情報収集完了: 合計 {len(all_articles)} 件の記事を取得")

    if not all_articles:
        logger.warning("⚠️ 記事が1件も取得できませんでした。終了します。")
        return

    # 重複URLを除去
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    logger.info(f"  重複除去後: {len(unique_articles)} 件")

    # ──────────────────────────────────────
    # Step 2: AI分析・フィルタリング
    # ──────────────────────────────────────
    logger.info("\n🤖 Step 2: AI分析・フィルタリング開始...")

    from src.ai.summarizer import ArticleSummarizer
    summarizer = ArticleSummarizer()
    analyzed_results = summarizer.analyze_batch(unique_articles)

    logger.info(f"\n✅ AI分析完了: {len(analyzed_results)} 件が採用基準を満たしました")

    if not analyzed_results:
        logger.info("📭 今日は適切なネタがありませんでした。")
        return

    # ──────────────────────────────────────
    # Step 3: Google Sheetsに書き込み
    # ──────────────────────────────────────
    logger.info("\n📊 Step 3: Google Sheetsに書き込み中...")

    from src.output.sheets import SheetsWriter
    writer = SheetsWriter()
    writer.write_results(analyzed_results)

    # ──────────────────────────────────────
    # 完了
    # ──────────────────────────────────────
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("\n" + "=" * 60)
    logger.info(f"🎉 処理完了！")
    logger.info(f"  📊 取得記事数: {len(all_articles)}")
    logger.info(f"  ✅ 採用記事数: {len(analyzed_results)}")
    logger.info(f"  ⏱️ 処理時間: {elapsed:.1f}秒")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
