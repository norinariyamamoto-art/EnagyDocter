# Energy Doctor LP Version 1.0 Integrated

Cloudflare PagesへDirect Uploadできる静的LP一式です。

## 公開方針
- サイトは先行公開できます。
- 初期状態では `config.js` の `receptionStatus: "closed"` により診断受付を停止します。
- 模擬案件・運用確認中は `"test"`、一般受付開始時は `"open"` に変更します。
- Microsoft FormsのURLは `publicFormUrl` / `testFormUrl` に設定します。
- 製品・サービスサイト完成後、`solutionUrls` を設定します。

## ファイル
- `index.html` LP本体
- `styles.css` デザイン
- `config.js` 受付状態・外部URL設定
- `script.js` CTA、モーダル、モバイルメニュー
- `assets/a3-report-p1.png`, `a3-report-p2.png` A3サンプル
- `assets/sawa-logo.png` 澤電気機械会社ロゴ

## Cloudflare Pages
このフォルダの内容をそのままDirect Uploadしてください。
想定サブドメイン: `energy-doctor.sawa-em.co.jp`

## 公開前確認
1. Energy Doctor正式B-3ロゴの画像データが確定したら、CSS描画ロゴを正式ロゴ画像へ差し替える。
2. Microsoft Forms URLを設定する。
3. 受付状態を確認する。
4. 製品・サービスリンクはサイト準備後に設定する。
5. noindex解除は本番公開方針確定時に実施する。
