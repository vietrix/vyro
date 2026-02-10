# トラブルシューティング

## `Invalid --app format`

`<module>:<attribute>` (例: `examples.hello_world:app`) を使用します。

## ルート署名エラー

ハンドラーが `async def` であり、最初の引数が `ctx` であることを確認してください。

## ネイティブ ビルドの問題

Rust ツールチェーンをインストールし、`maturin build --release` で再構築します。

## ドキュメントのビルド エラー

`mkdocs build --strict` を実行して、壊れたリンクや欠落しているページを修正します。