# デプロイメント

## チェックリスト

1.`VYRO_ENV=production`を設定します
2. 強力な `VYRO_SECRET_KEY` を構成する
3. CPU プロファイルからワーカー数を設定する
4. 可観測性と正常性プローブを有効にする
5. ロールアウト前に API コントラクトを検証する

## Kubernetes

マニフェストを生成します。

```bash
vyro k8s --name vyro-api --image ghcr.io/vietrix/vyro:latest --out k8s.yaml
```
