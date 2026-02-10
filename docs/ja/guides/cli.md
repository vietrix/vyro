# CLI ユーザーガイド

## コマンドモデル

Vyro CLI は 2 つのサーフェスに分割されています。

1. アプリケーションを実行および操作するためのエンドユーザー コマンド (`vyro ...`)。
2. 内部チェック/ビルド/ベンチ用の開発者スクリプト (`python -m scripts.dev...`)。

## エンドユーザーコマンド

- `vyro new` - 新しいプロジェクトの足場を作ります。
- `vyro run` - 実稼働スタイル モードでアプリを実行します。
- `vyro dev` - リロード動作でアプリを実行します。
- `vyro doctor` - 環境と準備のヒントを検証します。
- `vyro openapi` - アプリのルートから OpenAPI を生成します。
- `vyro compat` - API コントラクトを比較します。
- `vyro migrate` - 移行を実行します。
- `vyro drift` - スキーマのドリフトを検出します。
- `vyro k8s` - Kubernetes マニフェストを生成します。
- `vyro nogil-tune` - ワーカーのチューニングを推奨します。
- `vyro release ...` - 自動化コマンドをリリースします。

## 開発者専用スクリプト

これらは、エンドユーザーのランタイム操作ではなく、プロジェクトのメンテナンスに使用します。

```bash
python -m scripts.dev.check
python -m scripts.dev.test
python -m scripts.dev.build --sdist
python -m scripts.dev.bench --suite all --iterations 10000 --out bench.json
```

## 終了コード

- `0`: 成功
- `1`: 実行/ランタイム/ツールの失敗
- `2`: 無効なユーザー入力/引数