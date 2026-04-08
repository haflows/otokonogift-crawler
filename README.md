# otokonogift ネタ探し自動化クローラー

30-40代の男性が女性に贈って喜ばれるプレゼント・体験・イベント情報を、12の情報源から毎日自動収集するシステムです。

## 📋 情報源

| サイト | 取得する情報 |
|--------|-------------|
| PR TIMES | プレスリリース（新商品・イベント告知） |
| FASHION PRESS | ビューティー・グルメ・ファッション・イベント |
| Hanako Web | スイーツ・カフェ・お出かけスポット |
| sweet web | ファッション・コスメ・美容トレンド |
| OZmagazine | お出かけスポット・レストラン・リラクゼーション |
| 三越伊勢丹 | ギフト特集・限定品・新商品 |
| @cosme | コスメランキング・新商品 |
| 一休.com | 高級レストラン・スパ・ホテル体験 |
| Anny Magazine | ギフト専門メディア |
| 婦人画報 | 上質なグルメ・ギフト・ビューティー |
| Makuake | クラファンのユニークギフト |
| Googleトレンド | ギフト関連トレンドワード |

## 🚀 セットアップ

### 1. Python環境の準備

```bash
cd otokonogift-クローラー
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Gemini APIキーの取得（無料）

1. [Google AI Studio](https://aistudio.google.com/apikey) にアクセス
2. Googleアカウントでログイン
3. 「Get API Key」をクリック
4. APIキーをコピー

### 3. Google Sheetsの設定

#### 3-1. Google Cloud サービスアカウントの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（例: `otokonogift-crawler`）
3. 左メニュー → 「APIとサービス」→「ライブラリ」
4. 「Google Sheets API」を検索 → **有効にする**
5. 「Google Drive API」を検索 → **有効にする**
6. 左メニュー → 「APIとサービス」→「認証情報」
7. 「認証情報を作成」→「サービスアカウント」
8. 名前を入力（例: `otokonogift-sheets`）→ 作成
9. 作成されたサービスアカウントをクリック
10. 「鍵」タブ → 「鍵を追加」→「新しい鍵を作成」→ **JSON** → 作成
11. ダウンロードされたJSONファイルを安全に保管

#### 3-2. スプレッドシートの準備

1. [Google Sheets](https://sheets.google.com) で新規スプレッドシートを作成
2. 名前を「otokonogift ネタ帳」などに設定
3. URLから **スプレッドシートID** をコピー
   - URL例: `https://docs.google.com/spreadsheets/d/【このIDをコピー】/edit`
4. **共有設定**: サービスアカウントのメールアドレス（`xxx@xxx.iam.gserviceaccount.com`）を「編集者」として追加

### 4. 環境変数の設定

`.env.example` をコピーして `.env` を作成：

```bash
cp .env.example .env
```

`.env` を編集：

```
GEMINI_API_KEY=取得したAPIキー
GOOGLE_SHEETS_SPREADSHEET_ID=スプレッドシートID
GOOGLE_SERVICE_ACCOUNT_JSON=ダウンロードしたJSONファイルのパス
```

### 5. ローカルテスト

```bash
python main.py
```

## 🔄 GitHub Actionsでの自動実行

### 1. GitHubリポジトリの作成

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/otokonogift-crawler.git
git push -u origin main
```

### 2. シークレットの設定

GitHubリポジトリの Settings → Secrets and variables → Actions で以下を設定：

| シークレット名 | 値 |
|---------------|--- |
| `GEMINI_API_KEY` | Gemini APIキー |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | スプレッドシートID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | サービスアカウントJSONの**中身全体** |

### 3. 自動実行

- 毎朝8:00 JST に自動実行されます
- 手動実行: Actions → 「otokonogift Daily Crawler」→ 「Run workflow」

## 📊 出力フォーマット

スプレッドシートには月ごとのシートが自動作成され、以下のカラムで情報が記録されます：

| カラム | 内容 |
|--------|------|
| 日付 | 取得日 |
| カテゴリ | 絵文字付きカテゴリ |
| タイトル | 記事タイトル |
| 要約 | AI生成の100-200文字要約 |
| おすすめ度 | ★☆☆☆☆ 〜 ★★★★★ |
| 想定価格帯 | 円表記 |
| 情報源 | サイト名 |
| 元URL | リンク |
| 投稿ネタメモ | SNS投稿アイデア |
| ステータス | 未確認 / 確認済み / 投稿済み |
