"""
Google Sheets 出力モジュール
分析結果をスプレッドシートに書き込む
"""
import json
import logging
from datetime import datetime
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from config.settings import GOOGLE_SHEETS_SPREADSHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON

logger = logging.getLogger(__name__)

# Google Sheets APIのスコープ
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# シートのヘッダー定義
HEADERS = [
    "日付",
    "カテゴリ",
    "タイトル",
    "要約",
    "おすすめ度",
    "想定価格帯",
    "情報源",
    "元URL",
    "投稿ネタメモ",
    "ステータス",
]


class SheetsWriter:
    """Google Sheetsへの書き込みを管理"""

    def __init__(self):
        if not GOOGLE_SHEETS_SPREADSHEET_ID:
            raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID が設定されていません。")

        self.spreadsheet_id = GOOGLE_SHEETS_SPREADSHEET_ID
        self.client = self._authenticate()
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)

    def _authenticate(self) -> gspread.Client:
        """Google Sheets APIの認証"""
        try:
            # 環境変数にJSONが直接入っている場合（GitHub Actions用）
            if GOOGLE_SERVICE_ACCOUNT_JSON.startswith("{"):
                service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
                credentials = Credentials.from_service_account_info(
                    service_account_info, scopes=SCOPES
                )
            else:
                # ファイルパスの場合
                credentials = Credentials.from_service_account_file(
                    GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
                )
            return gspread.authorize(credentials)
        except Exception as e:
            logger.error(f"Google Sheets 認証エラー: {e}")
            raise

    def _get_or_create_sheet(self, sheet_name: str) -> gspread.Worksheet:
        """シートを取得（なければ作成）"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=len(HEADERS)
            )
            # ヘッダーを追加
            worksheet.update("A1", [HEADERS])
            # ヘッダー行のフォーマット
            worksheet.format("A1:J1", {
                "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.3},
                "textFormat": {
                    "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                    "bold": True,
                    "fontSize": 11,
                },
                "horizontalAlignment": "CENTER",
            })
            logger.info(f"シート「{sheet_name}」を作成しました")
        return worksheet

    def write_results(self, analyzed_results: list[tuple], sheet_name: Optional[str] = None):
        """
        分析結果をスプレッドシートに書き込む

        Args:
            analyzed_results: [(article, analysis_result), ...] のリスト
            sheet_name: シート名（デフォルトは今月の年月）
        """
        if not analyzed_results:
            logger.info("書き込む結果がありません")
            return

        # シート名（月ごとに分ける）
        if not sheet_name:
            sheet_name = datetime.now().strftime("%Y年%m月")

        worksheet = self._get_or_create_sheet(sheet_name)

        # 既存のURLを取得（重複防止）
        existing_urls = set()
        try:
            url_col = worksheet.col_values(8)  # 元URL列（H列）
            existing_urls = set(url_col[1:])  # ヘッダーを除外
        except Exception:
            pass

        # 書き込むデータを準備
        rows_to_add = []
        today = datetime.now().strftime("%Y/%m/%d")

        for article, result in analyzed_results:
            # 重複チェック
            if article.url in existing_urls:
                logger.debug(f"重複スキップ: {article.title}")
                continue

            # おすすめ度を星に変換
            stars = "★" * result.gift_score + "☆" * (5 - result.gift_score)

            row = [
                today,
                result.category_label,
                article.title,
                result.summary,
                stars,
                result.estimated_price or "不明",
                article.source_name,
                article.url,
                result.post_idea,
                "未確認",
            ]
            rows_to_add.append(row)

        if not rows_to_add:
            logger.info("新しい結果はありませんでした（全て重複）")
            return

        # バッチで書き込み
        try:
            # 次の空き行を見つける
            all_values = worksheet.get_all_values()
            next_row = len(all_values) + 1

            # 前回の書き込みと日付が変わっていれば、先頭に空行を挿入して可読性を高める
            if len(all_values) > 1:
                last_row_date = str(all_values[-1][0]).strip()
                if last_row_date and last_row_date != today:
                    rows_to_add.insert(0, [""] * len(HEADERS))

            # 一括書き込み
            cell_range = f"A{next_row}:J{next_row + len(rows_to_add) - 1}"
            worksheet.update(cell_range, rows_to_add)

            logger.info(f"✅ {len(rows_to_add)}件をシート「{sheet_name}」に書き込みました")
        except Exception as e:
            logger.error(f"Google Sheets 書き込みエラー: {e}")
            raise
