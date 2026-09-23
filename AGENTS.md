# invoice — 作業の入口

- /root/AGENTS.md、HANDOFF.md、IMPLEMENTATION.mdから始める。負荷は /root/products/運用ルール.md。
- 本体はpublic/index.html。本番はGitHub Pages、保存の正はlocalStorage。クラウド同期を保存元とみなさない。
- getStoredProfileData()とpersistProfile()を使い、編集中以外の取引先も保持する。inv_bak_*の5世代バックアップと旧キー移行を維持し、旧データを削除しない。
- 口座番号は必須・数字7桁。登録番号は任意・空欄またはT+13桁。不正時は明示保存/DLを止めても自動保存を継続し、データ損失を防ぐ。
- プロフィール切替・名前変更・削除の詳細はdocs/agent-context/rules-agents-20260923.md。初期プロフィールの改名禁止等を落とさない。
- 画面/PDFの文字の太さ・字間・寄せ・枠・改ページを両方目視確認する。font-familyの変更で決めつけず、スムージングと印刷の差を切り分ける。
- mainへのpushは本番公開を起動する。文書保存・コード検証と公開を混同しない。秘密・実請求データをGitへ入れない。
- 実行前説明、危険操作承認、相互レビュー、Git、FB要約報告は共通規則。再開はHANDOFF、判断はDECISIONS.md（必要時作成）。
# 決定の更新確認

DECISIONS.mdが存在する場合は開始時に読む。保全した過去規約より新しい判断を取りこぼさない。存在しない場合は保全規約とHANDOFFの最新決定を使う。
