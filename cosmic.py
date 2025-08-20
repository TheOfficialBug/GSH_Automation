import os
import requests
import base64
import tarfile
from tqdm import tqdm
from config.settings import DATA_DIR

# Define these constants based on the file we wanna downloaaaad
COSMIC_BUCKET = "downloads"
COSMIC_PATH = "grch37/cosmic/v102/Cosmic_CancerGeneCensus_Tsv_v102_GRCh37.tar"
COSMIC_API_URL = "https://cancer.sanger.ac.uk/api/mono/products/v1/downloads/scripted"

def download():
    email = input("Enter your COSMIC email: ").strip()
    password = input("Enter your COSMIC password: ").strip()

    # Step 1: encoooding the email:password with Base64 
    auth_str = f"{email}:{password}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    # Step 2: Requestingg for a pre-signed dwnldd URL
    headers = {
        "Authorization": f"Basic {encoded_auth}"
    }
    params = {
        "path": COSMIC_PATH,
        "bucket": COSMIC_BUCKET
    }

    print("🔐 Requesting a secure download URL...")
    try:
        response = requests.get(COSMIC_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        download_url = data.get("url")
        if not download_url:
            print("❌ 'download_url' not found in the response.")
            print("Response:", data)
            return
    except Exception as e:
        print(f"❌ Failed to retrieve download URL: {e}")
        return

    # Step 3: Download from the secure URL
    filename = os.path.basename(COSMIC_PATH)
    output_dir = os.path.join(DATA_DIR, "cosmic")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    print(f"⬇️ Downloading COSMIC file: {filename}")
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(output_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
        print(f"✅ COSMIC file downloaded successfully: {output_path}")
    except Exception as e:
        print(f"❌ Error downloading COSMIC file: {e}")
        return

    # Step 4: Extract the .tar file
    print("📦 Extracting the downloaded tar file...")
    try:
        with tarfile.open(output_path, "r") as tar:
            tar.extractall(path=output_dir)
        print(f"✅ Extraction complete. Files are in: {output_dir}")
    except Exception as e:
        print(f"❌ Error extracting tar file: {e}")
