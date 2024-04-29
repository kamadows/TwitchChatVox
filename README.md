# TwitchChatVox

## 目次
- [TwitchChatVox](#twitchchatvox)
  - [目次](#目次)
  - [概要](#概要)
  - [動作確認環境](#動作確認環境)
  - [インストール](#インストール)
  - [初期設定](#初期設定)
  - [使用方法](#使用方法)
    - [読み上げ機能の起動](#読み上げ機能の起動)
    - [話者の設定変更](#話者の設定変更)
    - [HostとPortを変更している場合](#hostとportを変更している場合)
  - [ライセンス](#ライセンス)
  - [連絡先](#連絡先)

## 概要

このプロジェクトは、macOSでVOICEVOXを利用し、Twitchのチャットを音声で読み上げるためのソフトウェアです。

## 動作確認環境

- プロセッサ: Apple M3
- メモリ: 24GB
- OS: Sonoma 14.4.1
- VOICEVOX バージョン: 0.19.0
- SHAREVOX バージョン: 0.2.1
- COEIROINKv2 バージョン: 2.3.4

## インストール

TwitchChatVOXを利用するためには、まずMacにPortAudioが必要です。brewなどでインストールしてください。

```bash
brew install portaudio
```

仮想環境を使用することを推奨してます。
仮想環境を作成してアクティベートします。
その後GitHubからリポジトリをクローン、そして必要なパッケージをインストールします。

```bash
python3 -m venv twitchchatvox-env
source twitchchatvox-env/bin/activate
git clone https://github.com/kamadows/TwitchChatVox.git
cd TwitchChatVox
pip install -r requirements.txt
```

## 初期設定

このプログラムはTwitchのチャット取得にTwitchIOを使用しています。
そのためOAuthパスワードを取得する必要があります。
以下のサイトからOAuthパスワードを取得してください。

[Twitch Chat OAuth Password Generator](https://twitchapps.com/tmi/)

先ほど取得したパスワードをconfig/twitch_config.pyのTWITCH_ACCESS_TOKEN、配信するアカウント名をLOGIN_CHANNELに書き込んでください

```
TWITCH_ACCESS_TOKEN = "ここにOAuthパスワード"
LOGIN_CHANNEL = "ここにアカウント名"
COMMAND_PREFIX = "!"
```

## 使用方法

このプログラムを使用する前にVOICEVOX、または派生ソフトを起動しておいてください。

### 読み上げ機能の起動

VOICEVOXで読み上げさせたい場合、voicevox_twitch_chat.pyを使用してください。

```bash
python3 src/voicevox_twitch_chat.py
```

### 話者の設定変更

話者とconfig/character_config.pyに設定があります。
編集してstyleIdを使用したいキャラクターのidにすることで読み上げキャラクターが変更されます。

idを調べるには、src/voicevox_list_speakers.pyを使用してください。
speaker_dataにキャラと対応idが出力されます。
関連ソフトも同時に起動していると出力されます。

```bash
python3 src/voicevox_list_speakers.py
```

COEIROINKv2はsrc/voicevox_list_speakers.pyを使用してください。
UUIDとstyleIDが出力されるので、そちらをお使いください。

```bash
python3 src/coeiroink_list_speakers.py
```

### HostとPortを変更している場合

変更していない場合、いじる必要はありません。
変更している場合、config/servers.pyを編集してください。

## ライセンス

Copyright (c) 2024 Cre8Arts
Released under the MIT license
https://opensource.org/licenses/mit-license.php


## 連絡先

プロジェクトに関する質問やフィードバックは、以下のXアカウントを通じてお寄せください。

[Xアカウント](https://x.com/kamadows)