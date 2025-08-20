import os, tarfile, requests, shutil
from config.settings import ENHANCERATLAS_URL, DATA_DIR
from tqdm import tqdm

def download():
    target_dir = os.path.join(DATA_DIR, "enhanceratlas")
    os.makedirs(target_dir, exist_ok=True)
    tar_path = os.path.join(target_dir, "species_enh_bed.tar.gz")

    with requests.get(ENHANCERATLAS_URL, stream=True) as r:
        with open(tar_path, "wb") as f, tqdm(total=int(r.headers.get('content-length', 0)), unit='B', unit_scale=True) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

    print("Extracting and cleaning up enhancer BED files...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=target_dir)

    for file in os.listdir(target_dir):
        if file.endswith(".bed") and file != "dr.bed":
            os.remove(os.path.join(target_dir, file))
    print("EnhancerAtlas 'dr.bed' retained.")