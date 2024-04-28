import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import asyncio
import httpx
from twitchio.ext import commands
from config.servers import SERVERS
from config.twitch_config import TWITCH_ACCESS_TOKEN, LOGIN_CHANNEL, COMMAND_PREFIX
from config.character_config import CHARACTER, volume
import requests, json
import io
import wave
import pyaudio
import time
import numpy as np

class Sharevox:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def speak(self, text, speaker, volume=None):
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
            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
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

class Bot(commands.Bot):
    def __init__(self, sv):
        super().__init__(token=TWITCH_ACCESS_TOKEN, prefix=COMMAND_PREFIX, initial_channels=[LOGIN_CHANNEL])
        self.sv = sv

    async def event_ready(self):
        print(f"Logged in as {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return
        print(f"Received message: {message.content}")
        if not message.content.startswith(COMMAND_PREFIX):
            self.sv.speak(message.content, speaker="SHAREVOX", volume=volume)

def main():
    sharevox_config = SERVERS.get("SHAREVOX")
    if sharevox_config:
        host = sharevox_config.get("host")
        port = sharevox_config.get("port")
    else:
        raise ValueError("Soicevox configuration not found in SERVERS")

    sv = Sharevox(host, port)
    bot = Bot(sv)
    bot.run()

if __name__ == "__main__":
    main()