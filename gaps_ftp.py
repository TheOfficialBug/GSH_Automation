import ftplib
import gzip
import shutil
import os

def download_ucsc_gap_data(assembly="danRer11", table_name="gap", out_dir="data/ucsc_gap"):
    ftp_host = "hgdownload.soe.ucsc.edu"
    ftp_path = f"/goldenPath/{assembly}/database"
    filename_gz = f"{table_name}.txt.gz"
    filename_tsv = f"{table_name}.tsv"

    os.makedirs(out_dir, exist_ok=True)
    local_gz_path = os.path.join(out_dir, filename_gz)
    local_tsv_path = os.path.join(out_dir, filename_tsv)

    print(f"Connecting to UCSC FTP: {ftp_host} .....")
    with ftplib.FTP(ftp_host) as ftp:
        ftp.login()
        ftp.cwd(ftp_path)
        print(f"[INFO] Downloading {filename_gz} ...")
        with open(local_gz_path, "wb") as f:
            ftp.retrbinary(f"RETR {filename_gz}", f.write)

    print(f"Extracting to {filename_tsv} ...")
    with gzip.open(local_gz_path, "rb") as f_in:
        with open(local_tsv_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.remove(local_gz_path)
    print(f"[DONE] Gap track data saved to: {local_tsv_path}")