import os
import sys
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.servers import COEIROINK_SERVERS

class Coeiroink:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def fetch_speakers(self, server_name):
        url = f"http://{self.host}:{self.port}/v1/speakers"
        response = requests.get(url)
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'speaker_data')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, f'{server_name}_speakers_list.txt')
        with open(output_file_path, "w") as file:
            if response.status_code == 200:
                speakers = response.json()
                for speaker in speakers:
                    file.write("\n" + "=" * 30 + "\n")
                    file.write(f"Name: {speaker['speakerName']}\n")
                    file.write(f"Speaker UUID: {speaker['speakerUuid']}\n")
                    styles = speaker['styles']
                    file.write('styles:\n')
                    for style in styles:
                        file.write(f"     {style['styleId']:>4} : {style['styleName']}\n")
            else:
                file.write(f"Failed to fetch speakers from {server_name}: Status code {response.status_code}\n")

def main():
    server_name = "COEIROINK"
    vv = Coeiroink(COEIROINK_SERVERS["host"], COEIROINK_SERVERS["port"])
    vv.fetch_speakers(server_name)

if __name__ == "__main__":
    main()
