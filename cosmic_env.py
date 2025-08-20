import os, base64, requests, tarfile
from dotenv import load_dotenv
from config.settings import DATA_DIR

def download_cosmic_file():
    # Load environment variables from .env file
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

    # Get credentials from environment
    email = os.getenv("COSMIC_EMAIL")
    password = os.getenv("COSMIC_PASSWORD")

    if not email or not password:
        raise ValueError("Missing COSMIC_EMAIL or COSMIC_PASSWORD in environment variables")

    # Step 1: Encode email:password to base64
    auth_string = f"{email}:{password}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()

    # Step 2: Request the temporary download URL
    download_api = (
        "https://cancer.sanger.ac.uk/api/mono/products/v1/downloads/scripted"
        "?path=grch37/cosmic/v102/Cosmic_CancerGeneCensus_Tsv_v102_GRCh37.tar&bucket=downloads"
    )

    headers = {
        "Authorization": f"Basic {auth_base64}"
    }

    print("🔗 Requesting temporary download URL from COSMIC...")
    response = requests.get(download_api, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get download URL:", response.text)
        return

    download_url = response.json().get("url")
    if not download_url:
        print("❌ Download URL not found in response.")
        return

    # Step 3: Download the file
    output_dir = os.path.join(DATA_DIR, "cosmic")
    os.makedirs(output_dir, exist_ok=True)
    tar_filename = os.path.join(output_dir, "Cosmic_CancerGeneCensus_Tsv_v102_GRCh37.tar")

    print(f"⬇️ Downloading file to: {tar_filename}")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(tar_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"✅ Download complete: {tar_filename}")

    # Step 4: Extract the tar file
    print("📦 Extracting .tar file...")
    try:
        with tarfile.open(tar_filename, "r") as tar:
            tar.extractall(path=output_dir)
        print(f"✅ Extraction complete. Files extracted to: {output_dir}")
    except Exception as e:
        print(f"❌ Failed to extract .tar file: {e}")
