# インストール

＃＃ 要件

- Python 3.10+
- ピップ
- Rust ツールチェーン (ソース ビルドにのみ必要)

## PyPI からインストールする

```bash
pip install vyro
```

## インストールを確認する

プライマリ (エンド ユーザーに推奨):

```bash
vyro --help
```

フォールバック (シェル PATH がまだ `vyro` を公開していない場合):

```bash
python -m vyro --help
```

## なぜ 2 つのコマンドがあるのでしょうか?

- `vyro` は、公式のエンドユーザー CLI コマンドです。
- `python -m vyro` は同じ CLI モジュールを直接実行し、PATH/デバッグ シナリオに役立ちます。

## PATH のトラブルシューティング

`vyro` が見つからない場合:

1. インストール後にターミナルを再度開きます。
2. Python Scripts ディレクトリが PATH 上にあることを確認します。
3. `python -m vyro` を一時的に使用します。

## 開発者のセットアップ

```bash
pip install -e .[dev]
pip install -e .[docs]
```
