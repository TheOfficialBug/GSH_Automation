import os, requests
from config.settings import HUMAN_ORTHO_URL, DATA_DIR, HTTP_STATUS_CODES
from tqdm import tqdm

def download():
    target_dir = os.path.join(DATA_DIR, "orthologs")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, "human_orthos.txt")

    # Skip download if the fileee already existzz
    if os.path.exists(filepath):
        print(f"Orthologs data already exists at {filepath}")
        return filepath

    # Make request and check response
    try:
        response = requests.get(HUMAN_ORTHO_URL, stream=True)
        status_code = response.status_code
        if status_code != 200:
            msg = HTTP_STATUS_CODES.get(status_code, f"Unexpected error with status code {status_code}")
            raise Exception(f"❌ Failed to download Orthologs data: {msg}")
    except Exception as e:
        print(str(e))
        return None

    # Save file with progress bar
    total_size = int(response.headers.get('content-length', 0))
    with open(filepath, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    print("✅ Orthologs data downloaded.")
    return filepath
