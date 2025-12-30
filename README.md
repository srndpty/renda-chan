# renda-chan

## ホットキー登録に必要な権限

このアプリは `pynput` または `keyboard` を使って開始/停止ホットキーを登録します。
OS によって追加の権限や設定が必要です。

- macOS: システム設定 → プライバシーとセキュリティ → アクセシビリティ / 入力監視で許可を付与してください。
- Windows: グローバルホットキーのフックに管理者権限が必要な場合があります。
- Linux: `/dev/uinput` の権限付与や `input` グループへの追加が必要になることがあります。

## 開発中の実行方法

依存関係をインストールした後、仮想環境をアクティブにして以下のコマンドで実行します。

```bash
python -m src.main
```

## Windows 向けビルド手順 (PyInstaller)

1. 依存関係をインストールします。

   ```bash
   python -m pip install --upgrade pip
   python -m pip install pyinstaller pyqt6 pynput keyboard
   ```

2. ビルドを実行します。

   ```bash
   pyinstaller pyinstaller.spec
   ```

3. `dist/renda-chan.exe` が生成されます。アイコンは `assets/renda-chan.ico` を差し替えることで変更できます。

