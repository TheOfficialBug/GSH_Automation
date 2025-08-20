import os, requests, tarfile, zipfile
from tqdm import tqdm
from config.settings import DATA_DIR, LNC_RNA_URL, T_RNA_URL

def download_file(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    local_filename = os.path.join(output_dir, url.split('/')[-1])
    
    # Checkingg if thee file already exists
    if os.path.exists(local_filename):
        print(f"✅ File already exists: {local_filename}")
        return local_filename
    
    print(f"⬇️ Downloading {url.split('/')[-1]} ...")
    with requests.get(url, stream=True, verify=False) as r:  # verify=False since certificate was throwing an error
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        with open(local_filename, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))
    print(f"✅ Downloaded {local_filename}")
    return local_filename

def extract_file(filepath, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    if filepath.endswith(".zip"):
        print(f"📦 Extracting ZIP {filepath} ...")
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif filepath.endswith((".tar.gz", ".tgz")):
        print(f"📦 Extracting TAR.GZ {filepath} ...")
        with tarfile.open(filepath, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)
    else:
        print(f"No extraction performed for {filepath} (unsupported format). Check again")

def main():
    output_dir = os.path.join(DATA_DIR, "rna_files")

    # Download & extract lncRNA
    lnc_path = download_file(LNC_RNA_URL, output_dir)
    extract_file(lnc_path, output_dir)

    # Download & extract tRNA
    trna_path = download_file(T_RNA_URL, output_dir)
    extract_file(trna_path, output_dir)

if __name__ == "__main__":
    main()
