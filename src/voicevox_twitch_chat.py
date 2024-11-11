import os
import sys
import re

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 非同期処理やHTTPリクエスト関連のライブラリ
import asyncio
import httpx
from twitchio.ext import commands

# 設定ファイルのインポート
from config.servers import SERVERS
from config.twitch_config import TWITCH_ACCESS_TOKEN, LOGIN_CHANNEL, COMMAND_PREFIX, URL_REPLACEMENT, ENABLE_URL_REPLACEMENT, MAX_CHAR_COUNT, ENABLE_MAX_CHAR_COUNT, EXCLUDE_EMOTES
from config.character_config import CHARACTER, volume

# 音声関連のライブラリ
import requests, json
import io
import wave
import pyaudio
import time
import numpy as np

# Voicevoxクラス（テキストを音声に変換）
class Voicevox:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    # テキストを音声に変換して再生
    def speak(self, text, speaker, volume):
        params = (("text", text), ("speaker", CHARACTER.get(speaker, {}).get("styleId")))
        init_q = requests.post(f"http://{self.host}:{self.port}/audio_query", params=params)
        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )
        audio = io.BytesIO(res.content)
        with wave.open(audio, 'rb') as f:
            p = pyaudio.PyAudio()

            # コールバックで音声再生
            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                data_np = np.frombuffer(data, dtype=np.int16)
                data_np = data_np * volume
                data = data_np.astype(np.int16).tobytes()
                return (data, pyaudio.paContinue)

            stream = p.open(
                format=p.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(),
                rate=f.getframerate(),
                output=True,
                stream_callback=_callback
            )
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)
            stream.stop_stream()
            stream.close()
            p.terminate()

# Botクラス（Twitchチャットボット）
class Bot(commands.Bot):
    def __init__(self, vv):
        super().__init__(token=TWITCH_ACCESS_TOKEN, prefix=COMMAND_PREFIX, initial_channels=[LOGIN_CHANNEL])
        self.vv = vv

    # Botがログイン完了時に呼び出される
    async def event_ready(self):
        print(f"Logged in as {self.nick}")

    # メッセージ受信時の処理
    async def event_message(self, message):
        if message.echo:
            return
        print(f"Received message: {message.content}")
        
        if not message.content.startswith(COMMAND_PREFIX):
            processed_message = message.content

            # emotesの除去
            # processed_messageは上書き
            if EXCLUDE_EMOTES:
                processed_message = self.remove_emotes(message)

            # URL置換
            if ENABLE_URL_REPLACEMENT:
                processed_message = re.sub(r'https?://\S+|http?://\S+', URL_REPLACEMENT, processed_message)

            # 文字数制限
            if ENABLE_MAX_CHAR_COUNT and len(processed_message) > MAX_CHAR_COUNT:
                processed_message = processed_message[:MAX_CHAR_COUNT]

            # 音声再生
            self.vv.speak(processed_message, speaker="VOICEVOX", volume=volume)

    def remove_emotes(self, message):
        clean_message = message.content
        if message.tags['emotes']:
            emote_ranges = []
            # 'emotes': 'emotesv2_dcd06b30a5c24f6eb871e8f5edbd44f7:0-8,10-18,20-28/112290:53-60,62-69,71-78'みたいな感じなので、
            # [(0, 8), (10, 18), (20, 28), (53, 60), (62, 69), (71, 78)]だけ抜き出し。
            for emote in message.tags['emotes'].split('/'):
                for range_pair in emote.split(':')[1].split(','):
                    start, end = map(int, range_pair.split('-'))
                    emote_ranges.append((start, end))
            # 除去作業。 後ろから。
            for start, end in sorted(emote_ranges, reverse=True):
                clean_message = clean_message[:start] + clean_message[end+1:]

        return clean_message

# メイン関数
def main():
    voicevox_config = SERVERS.get("VOICEVOX")
    if voicevox_config:
        host = voicevox_config.get("host")
        port = voicevox_config.get("port")
    else:
        raise ValueError("Voicevox configuration not found in SERVERS")

    vv = Voicevox(host, port)
    bot = Bot(vv)
    bot.run()

if __name__ == "__main__":
    main()
