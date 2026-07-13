
import urllib.request
import os
import time

url = 'https://download-r2.pytorch.org/whl/cpu/torch-2.12.1%2Bcpu-cp313-cp313-win_amd64.whl'
file_name = 'torch.whl'

print(f'Starting download of {file_name} from {url}')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        total_length = response.length
        print(f'Total size: {total_length / 1024 / 1024:.2f} MB')
        with open(file_name, 'ab') as f:
            downloaded = os.path.getsize(file_name) if os.path.exists(file_name) else 0
            if downloaded > 0:
                print(f'Resuming from {downloaded} bytes')
                req.add_header('Range', f'bytes={downloaded}-')
                response = urllib.request.urlopen(req)
            
            chunk_size = 1024 * 1024
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                print(f'Downloaded {downloaded / 1024 / 1024:.2f} MB / {total_length / 1024 / 1024:.2f} MB', end='\r')
except Exception as e:
    print(f'\nError: {e}')

