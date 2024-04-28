import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import asyncio
from twitchio.ext import commands
from config.twitch_config import TWITCH_ACCESS_TOKEN, LOGIN_CHANNEL, COMMAND_PREFIX
from config.character_config import CHARACTER, volume
from config.servers import COEIROINK_SERVERS
import httpx
import io
import wave
import pyaudio
import numpy as np

class Coeiroink:
    def __init__(self):
        host = COEIROINK_SERVERS["host"]
        port = COEIROINK_SERVERS["port"]
        self.api_url = f"http://{host}:{port}/v1/predict"
        self.speaker_uuid = CHARACTER["COEIROINK"]["UUID"]
        self.style_id = CHARACTER["COEIROINK"]["styleId"]

    async def speak(self, text, volume):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={
                    'text': text,
                    'speakerUuid': self.speaker_uuid,
                    'styleId': self.style_id,
                    'prosodyDetail': None,
                    'speedScale': 1
                })

            if response.status_code != 200:
                print(f"API request failed with status code {response.status_code}")
                return

            audio_data = response.content
            self.play_audio(audio_data, volume)

    def play_audio(self, audio_data, volume):
        audio = io.BytesIO(audio_data)
        with wave.open(audio, 'rb') as f:
            p = pyaudio.PyAudio()
            try:
                stream = p.open(
                    format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True
                )
                while data := f.readframes(1024):
                    data_np = np.frombuffer(data, dtype=np.int16) * volume
                    stream.write(data_np.astype(np.int16).tobytes())
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_ACCESS_TOKEN, prefix=COMMAND_PREFIX, initial_channels=[LOGIN_CHANNEL])
        self.co = Coeiroink()

    async def event_ready(self):
        print(f"Logged in as {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return
        print(f"Received message: {message.content}")
        if not message.content.startswith(COMMAND_PREFIX):
            await self.co.speak(message.content, volume=volume)

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
