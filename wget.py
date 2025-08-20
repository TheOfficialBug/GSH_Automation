from pathlib import Path
import urllib.request
import pandas as pd

# Constants
URL = "https://hgdownload.soe.ucsc.edu/goldenPath/danRer11/bigZips/danRer11.chrom.sizes"
TARGET_DIR = Path("data/ucsc_chrominfo")
TARGET_DIR.mkdir(parents=True, exist_ok=True)

ORIG_FILE = TARGET_DIR / "danRer11.chrom.sizes"
CHROMINFO_TXT = TARGET_DIR / "chromInfo.txt"
CHROMINFO_ZG11 = TARGET_DIR / "chromInfo_zg11.txt"
ADD_CHROM_BED = TARGET_DIR / "add_chrom.bed"

def download_chrominfo():
    if all(f.exists() for f in [CHROMINFO_TXT, CHROMINFO_ZG11, ADD_CHROM_BED]):
        print("[✔] All files already exist.")
        return

    if not ORIG_FILE.exists():
        print("Downloading danRer11.chrom.sizes...")
        urllib.request.urlretrieve(URL, ORIG_FILE)
    else:
        print("[✔] danRer11.chrom.sizes already exists/downloaded.")

    # Rename/move to chromInfo.txt and chromInfo_zg11.txt
    if not CHROMINFO_TXT.exists():
        ORIG_FILE.rename(CHROMINFO_TXT)
        print("Renamed to chromInfo.txt")
    else:
        print("chromInfo.txt already exists.")

    if not CHROMINFO_ZG11.exists():
        CHROMINFO_TXT.rename(CHROMINFO_ZG11)
        print("Renamed to chromInfo_zg11.txt")
    else:
        print("file chromInfo_zg11.txt already exists.")


    print("Creating add_chrom.bed...")
    df = pd.read_csv(CHROMINFO_ZG11, sep="\t", header=None, names=["chrom", "end"])

    # insertingg start column at index 1
    df.insert(1, "start", 0)  
    df.to_csv(ADD_CHROM_BED, sep="\t", index=False, header=False)
    print("Created file add_chrom.bed under data dir")
