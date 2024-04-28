import requests
import json
import io
import wave
import pyaudio
import time
import numpy as np

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from config.servers import SERVERS
from config.character_config import CHARACTER, volume

class Voicevox:
    def __init__(self, host=SERVERS['VOICEVOX']['host'], port=SERVERS['VOICEVOX']['port']):
        self.host = host
        self.port = port

    def speak(self, text=None, speaker=CHARACTER["VOICEVOX"]["styleId"], volume=volume):
        params = (("text", text), ("speaker", speaker))
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

def main():
    vv = Voicevox()
    vv.speak("一人の下人が、クソデカい羅生門の完全な真下で雨やみを気持ち悪いほどずっと待ちまくっていた。")

if __name__ == "__main__":
    main()