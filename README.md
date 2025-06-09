# 仮想デジタルヒューマン

このプロジェクトは、Pythonを使用した仮想デジタルヒューマンの実装です。

## 機能

- 音声合成（TTS）による日本語音声出力
- カメラを使用した顔検出
- 基本的な対話機能

## 必要条件

- Python 3.8以上
- macOS

## インストール方法

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. プログラムを実行:
```bash
python virtual_human.py
```

2. スペースキーを押すと、仮想デジタルヒューマンが話し始めます。

## 注意事項

- カメラへのアクセス許可が必要です
- 日本語音声パッケージがインストールされていることを確認してください

WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
