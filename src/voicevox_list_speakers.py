import os
import sys
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.servers import SERVERS

class Voicevox:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def fetch_speakers(self, server_name):
        url = f"http://{self.host}:{self.port}/speakers"
        response = requests.get(url)
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'speaker_data')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, f'{server_name}_speakers_list.txt')
        with open(output_file_path, "w") as file:
            if response.status_code == 200:
                speakers = response.json()
                for speaker in speakers:
                    file.write("\n" + "=" * 30 + "\n")
                    file.write(f"Name: {speaker['name']}\n")
                    file.write(f"Speaker UUID: {speaker['speaker_uuid']}\n")
                    file.write("styles:\n")
                    for style in speaker['styles']:
                        file.write(f"    {style['id']} : {style['name']}\n")
            else:
                file.write(f"Failed to fetch speakers from {server_name}: Status code {response.status_code}\n")

def main():
    for server_name, config in SERVERS.items():
        vv = Voicevox(config["host"], config["port"])
        vv.fetch_speakers(server_name)

if __name__ == "__main__":
    main()
