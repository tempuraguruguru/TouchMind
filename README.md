# TouchMind

現実の接触（NFC）をトリガーとし、その瞬間の「思考」と「文脈（時間・場所）」をベクトル化して構造化するライフログシステムです。単なるテキストの保存ではなく、自然言語処理（NLP）を用いて思考を意味空間にマッピングし、後から「思考の偏り」や「文脈ごとの傾向」を分析可能にすることを目指しています。

## 🛠 技術スタック

- **Backend Framework**: Python 3.1x / Django
- **Package Management**: Poetry
- **Database**: PostgreSQL
- **Vector Extension**: pgvector (Docker経由で構築)
- **NLP / Embedding**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Frontend**: HTML / JavaScript (Fetch API) / Web NFC (※iPhone環境を考慮し、現在はURLパラメータによるタグID取得にフォールバック中)

## 📦 環境構築 (Setup)

本プロジェクトはパッケージ管理に **Poetry**、データベース環境に **Docker** を使用しています。

### 1. リポジトリのクローンとパッケージのインストール
```bash
git clone [https://github.com/tempuraguruguru/TouchMind.git](https://github.com/tempuraguruguru/TouchMind.git)
cd TouchMind
poetry install