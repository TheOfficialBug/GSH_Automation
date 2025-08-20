import os
import requests
from tqdm import tqdm
from config.settings import DATA_DIR

def download_ucsc(filename="ucsc_refseq.tsv"):
    """Downloads NCBI RefSeq All table for Zebrafish from UCSC Table Browser."""

    url = "https://genome.ucsc.edu/cgi-bin/hgTables"
    target_dir = os.path.join(DATA_DIR, "ucsc")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, filename)

    if os.path.exists(filepath):
        print(f"✅ UCSC RefSeq data already exists at {filepath}")
        return filepath

    data = {
    "clade": "vertebrate",
    "org": "Zebrafish",
    "db": "danRer11",
    "hgta_group": "genes",
    "hgta_track": "ncbiRefSeq",
    "hgta_table": "ncbiRefSeq",
    "hgta_regionType": "genome",
    "position": "",
    "hgta_outputType": "allFields",
    "hgta_outFileName": filename,
    "boolshad.doNotRedirect": "1",
    "boolshad.sendToGalaxy": "0",
    "boolshad.sendToGreat": "0",
    "hgta_doPrint": "get output",      # for actual output
    "hgta_doTopSubmit": "get output"
}


    print("⏳ Downloading UCSC NCBI RefSeq table for Zebrafish...")
    r = requests.post(url, data=data, stream=True)
    r.raise_for_status()

    total = int(r.headers.get("content-length", 0))
    with open(filepath, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    print(f"✅ UCSC RefSeq data downloaded to {filepath}")
    return filepath
