# HANDOFF — invoice

整理日：2026-09-23。ここは再開用の短い入口。計測時点の状態を、現在の稼働・公開状態と混同しない。

## 2026-11-16 データ消失と再発防止（最新）

- 本番は Vercel（チーム kota10-githubs-projects、プロジェクト invoice-app、https://invoice-app-two-gamma.vercel.app）。GitHub `kota10-github/invoice` の main に入ると自動で本番反映。GitHub Pages は 404（使っていない）。
- `/root/bin/push-projects`（cron 毎時30分）が未コミットの変更も自動コミット・push するため、**編集途中でも毎時30分に本番へ出る**。作業は30分を跨がないか、跨ぐ前にコミット判断する。
- 事故：Chrome（kouta.10 のプロファイル）の localStorage から取引先データが消えた（最終利用 10/17 〜 11/16 の間。Mac の空き容量が残り3%で、ブラウザの自動削除の可能性が高いが未確定）。jsonblob の控えは 2026-07 以前に期限切れで消えており、どこにも残っていなかった。
- 復元：過去に書き出したPDF（~/Downloads の `請求書_<取引先>_<品目>_<発行元>.pdf`）から5社（ライズ・FSC・GA Partners・Minamo・AI ONE）を作り直し、5社とも小計・消費税・合計がPDFと一致することを確認。ライズと AI ONE は内税（税込価格で入力）。**口座番号は空欄**（AIは入力しないため、ユーザーが入れる）。
- 再発防止（コミット 1b3880f）：保存のたびに VPS の書き込み専用口 `https://133-117-73-120.sslip.io/invoice-backup` へ控えを送る（画面上部に「控え：VPSに保存済み（時刻）」、失敗時は赤字）。ブラウザへ永続保存を申請（Chrome が許可しない場合あり）。jsonblob 保存と `/api/blob` 転送は停止（ブラウザ内データより優先して上書きする作りで危険、口座情報を誰でも読める場所に置く形だった）。
- 受け口：`server/backup_receiver.py`（systemd `invoice-backup`、127.0.0.1:8791、Caddy の `handle /invoice-backup`）。許可オリジンは本番URLのみ、読み出し口なし。控えは `backups-data/YYYY/MM/DD/HHMMSS-<hash>.json` と `backups-data/latest.json`（Git対象外、6時間ごとの /root/backups スナップショットには入る）。古い控えは消さない。
- 復元手順：`backups-data/latest.json`（または日付の控え）の中身を、本番ページの開発者コンソールで `localStorage.setItem('inv_default_user', <JSON文字列>)` して再読み込み。上書き前に現在の値を `inv_bak_<時刻>` へ退避する。

## 現在地（2026-09-23 時点）

- /root/products/invoice、計測時HEADee076b9。public/index.htmlをGitHub Pagesへ公開する静的アプリ。
- 保存はlocalStorage。過去にプロフィール消失事故があり、旧キー移行・保存の集約・5世代バックアップが必須。
- 今回は公開・保存データを変更していない。npm run buildはechoのみ、0.19秒。機能検証が成功した意味ではない。

## 再開順・残件

1. git status、依頼対象のUIと保存経路を確認する。main pushは本番公開なので文書保存でも注意する。
2. 依頼を受けたらIMPLEMENTATIONの情報を揃え、テスト用データで保存・切替・入力検証を試す。
3. 画面とPDFを同条件で比較し、寄せ・文字・余白まで確認する。
4. 過去HANDOFFの「未コミット/未デプロイ」と後続の「配布済み」は経緯として保存。今回新規の機能開発依頼はない。古いworktreeを不要と推測して削除しない。

## 完全な経緯と取りこぼし防止

整理前の全文は docs/agent-context/handoff-20260923.md に保全した。未完了・保留・判断待ちは削除していない。新しい依頼の対象語と「未完了・未決・未確認・残課題・対応中」で該当箇所を検索し、後続の完了記録・現物と照合する。明記がないものを完了扱いしない。

細かい完了経緯・過去の数値・検証証跡を毎回読む本文から移したが、記録自体は省略していない。新しい状態はこのファイルへ、長い証跡は対象の詳細資料へ記録する。
