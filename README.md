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

- **Mac Poetryの導入**
    1. homebrewのインストール（各自、調べてインストール）
    2. homebrewでpythonのインストール
        ```jsx
        brew install python
        ```
    3. Appleが提供しているpythonではないことを確認（Macにはすでにpythonがインストールされているが、これはあまり使えない）
        以下を入力して、python 3.13.xx以上であることを確認
        ```jsx
        echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
        ```
    4. Poetryをインストール
        ```jsx
        curl -sSL https://install.python-poetry.org | python3 -
        ```
    5. Path
        Poetryのインストール先が `$HOME/.local/bin` になっている場合、`$PATH` に追加する必要がある
        ```jsx
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
        ```
    **【注意点】**
    **プロジェクトの名前(project.name)に空白はだめ**

- **poetryの仮想環境のアクティベート**
    1. 仮想環境をアクティベートするPythonを指定します
        ```jsx
        poetry env use python3.11  # 例: 使用したいPythonのバージョン
        ```
    2. 仮想環境のパスを確認
        ```jsx
        poetry env info --path
        ```
    3. 仮想環境をアクティベート
        ```jsx
        source $(poetry env info --path)/bin/activate
        ```

- **Dockerのインストール**
    1. https://www.docker.com/products/docker-desktop/
    2. docker-compose.yml の作成（このプログラムでは、リポジトリをクローンすればOK）
    3. データベース起動
        ```bash
            docker compose up -d
        ```
        （※ docker ps と打って、ankane/pgvector が動いていれば成功）


### 1. リポジトリのクローンとパッケージのインストール
- GitHub（リモートリポジトリ）にあるプログラムをPC（ローカルリポジトリ）にコピー（クローン）し、このプログラムで使っているPoetry環境を適用
```bash
git clone [https://github.com/tempuraguruguru/TouchMind.git](https://github.com/tempuraguruguru/TouchMind.git)
cd TouchMind
poetry install
```
- 新しくライブラリを追加する場合は以下のコマンド
```jsx
    poetry add library_name
```