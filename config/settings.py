"""
otokonogift ネタ探し自動化 - 設定ファイル
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Gemini API
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-lite"

# ──────────────────────────────────────────────
# Google Sheets
# ──────────────────────────────────────────────
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")

# ──────────────────────────────────────────────
# スクレイピング設定
# ──────────────────────────────────────────────
REQUEST_TIMEOUT = 15  # seconds
REQUEST_DELAY = 2  # seconds between requests (礼儀正しいスクレイピング)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
MAX_ARTICLES_PER_SOURCE = 10  # 各サイトから取得する最大記事数

# ──────────────────────────────────────────────
# フィルタリング設定
# ──────────────────────────────────────────────
PRICE_RANGE_MIN = 1000  # 円
PRICE_RANGE_MAX = 50000  # 円

# ──────────────────────────────────────────────
# カテゴリ定義
# ──────────────────────────────────────────────
CATEGORIES = {
    "new_product": "🎁新商品",
    "cosmetics": "💄コスメ・美容",
    "sweets": "🍰スイーツ・グルメ",
    "event": "🎪イベント・スポット",
    "limited": "🎀限定品・コラボ",
    "experience": "💝体験ギフト",
    "fashion": "👗ファッション",
    "other": "📌その他",
}

# ──────────────────────────────────────────────
# 情報源定義
# ──────────────────────────────────────────────
SOURCES = {
    "prtimes": {
        "name": "PR TIMES",
        "url": "https://prtimes.jp",
        "enabled": True,
    },
    "fashion_press": {
        "name": "FASHION PRESS",
        "url": "https://www.fashion-press.net",
        "enabled": True,
    },
    "hanako": {
        "name": "Hanako Web",
        "url": "https://hanako.tokyo",
        "enabled": True,
    },
    "sweet": {
        "name": "sweet web",
        "url": "https://sweetweb.jp",
        "enabled": True,
    },
    "ozmagazine": {
        "name": "OZmagazine",
        "url": "https://www.ozmall.co.jp/ozmagazine",
        "enabled": True,
    },
    "mistore": {
        "name": "三越伊勢丹",
        "url": "https://www.mistore.jp/shopping",
        "enabled": True,
    },
    "cosme": {
        "name": "@cosme",
        "url": "https://www.cosme.net",
        "enabled": True,
    },
    "ikyu": {
        "name": "一休.com",
        "url": "https://www.ikyu.com",
        "enabled": True,
    },
    "anny": {
        "name": "Anny Magazine",
        "url": "https://anny.gift",
        "enabled": True,
    },
    "fujingaho": {
        "name": "婦人画報",
        "url": "https://www.fujingaho.jp",
        "enabled": True,
    },
    "makuake": {
        "name": "Makuake",
        "url": "https://www.makuake.com",
        "enabled": True,
    },
    "google_trends": {
        "name": "Googleトレンド",
        "url": "https://trends.google.co.jp",
        "enabled": True,
    },
}

# ──────────────────────────────────────────────
# AI プロンプト
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """あなたは「otokonogift」というSNSアカウントのコンテンツリサーチャーです。

【アカウントのテーマ】
30〜40代の男性が、女性（恋人・妻・女性の友人・女性の同僚）に贈って喜ばれる
プレゼント・体験・イベント情報を発信するアカウントです。

【あなたの役割】
収集した記事・情報を分析し、以下を判定してください：

1. **ギフト適合度**（1-5）: 30-40代男性が女性に贈るギフトとしてどれだけ適切か
2. **カテゴリ**: new_product / cosmetics / sweets / event / limited / experience / fashion / other
3. **要約**: 100-200文字の日本語要約（男性読者向けに書く）
4. **投稿ネタメモ**: このネタをSNSで紹介する場合の一言アイデア
5. **想定価格帯**: 分かる場合のみ（例: "3,000円〜5,000円"）

【採用基準】
✅ 女性が喜ぶスイーツ・コスメ・アクセサリー・ファッション小物
✅ カップルで楽しめるイベント・スポット・レストラン
✅ 季節の限定品・コラボ商品
✅ 体験ギフト（スパ、アフタヌーンティー、レストランなど）
✅ 話題のポップアップストア・展覧会
✅ 価格帯: 1,000円〜50,000円

【除外基準】
❌ 下着・ランジェリー類
❌ 過度にパーソナルなアイテム（ただしブランド香水は可）
❌ 日用品（洗剤、掃除用品等）
❌ 男性のみが興味を持つ情報（ガジェット、車、バイク等）
❌ 子供向け商品
❌ 価格が1,000円未満 or 50,000円超

ギフト適合度が2以下の場合は、その情報は不適切と判断してください。
"""

ANALYSIS_PROMPT_TEMPLATE = """以下の記事情報を分析してください。

【情報源】{source_name}
【タイトル】{title}
【URL】{url}
【本文（抜粋）】
{content}

上記の情報を分析し、以下のJSON形式で回答してください：
{{
    "is_relevant": true/false,
    "gift_score": 1-5の数値,
    "category": "カテゴリキー",
    "summary": "100-200文字の要約",
    "post_idea": "SNS投稿アイデア一言",
    "estimated_price": "想定価格帯（不明な場合はnull）"
}}

is_relevantがfalseの場合、他のフィールドは空でOKです。
"""
