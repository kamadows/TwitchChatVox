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
from config.servers import COEIROINK_SERVERS
from config.character_config import CHARACTER, volume


class Coeiroink:
    def __init__(self, host=COEIROINK_SERVERS['host'], port=COEIROINK_SERVERS['port'], speaker_uuid=CHARACTER['COEIROINK']['UUID'], style_id=CHARACTER['COEIROINK']['styleId']):
        
        self.api_url = f'http://{host}:{port}/v1/predict'
        self.speaker_uuid = speaker_uuid
        self.style_id = style_id

    def speak(self, text=None, volume=volume):
        response = requests.post(
            self.api_url,
            json={
                'text': text,
                'speakerUuid': self.speaker_uuid,
                'styleId': self.style_id,
                'prosodyDetail': None,
                'speedScale': 1
            })
        audio = io.BytesIO(response.content)
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
            while stream.is_active():  # ここを修正しました
                time.sleep(0.1)
            stream.stop_stream()
            stream.close()
            p.terminate()

def main():
    text_to_speech = "ある日の超暮方(ほぼ夜)の事である。一人の下人が、クソデカい羅生門の完全な真下で雨やみを気持ち悪いほどずっと待ちまくっていた。"
    co = Coeiroink()
    co.speak(text_to_speech)

if __name__ == "__main__":
    main()