import os
import requests
import gzip
import shutil
from config.settings import ENSEMBL_FTP_BASE, DATA_DIR
from tqdm import tqdm

def get_latest_release():
    try:
        response = requests.get("https://rest.ensembl.org/info/data?content-type=application/json")
        if response.ok:
            data = response.json()
            return max(data.get("releases", []))
    except Exception as e:
        print(f"Failed to fetch Ensembl release: {e}")
    return None

def extract_and_delete_gzip(file_path):
    """Extract .gz file, delete archive, and return extracted filename."""
    extracted_path = file_path.rstrip('.gz')
    try:
        with gzip.open(file_path, 'rb') as f_in:
            with open(extracted_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file_path)  # <--- Delete the .gz file after extraction
        print(f"Extracted and removed archive: {file_path}")
        return extracted_path
    except Exception as e:
        print(f"Failed to extract {file_path}: {e}")
        return None

def add_chr_prefix_to_fasta(file_path):
    """Add 'chr' prefix to FASTA headers (lines starting with '>') in-place."""
    temp_file = file_path + ".tmp"
    try:
        with open(file_path, 'r') as infile, open(temp_file, 'w') as outfile:
            for line in infile:
                if line.startswith('>'):
                    line = line.replace('>', '>chr', 1)
                outfile.write(line)
        os.replace(temp_file, file_path)  # Overwrite original file
        print(f"Added 'chr' prefix to FASTA headers in {file_path}")
    except Exception as e:
        print(f"Failed to update FASTA headers in {file_path}: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

def download():
    release = get_latest_release()
    if not release:
        print("Could not determine the latest release.")
        return

    urls = {
        f"Danio_rerio.GRCz11.{release}.gtf.gz": f"{ENSEMBL_FTP_BASE}release-{release}/gtf/danio_rerio/Danio_rerio.GRCz11.{release}.gtf.gz",
        f"Danio_rerio.GRCz11.dna.primary_assembly.fa.gz": f"{ENSEMBL_FTP_BASE}release-{release}/fasta/danio_rerio/dna/Danio_rerio.GRCz11.dna.primary_assembly.fa.gz",

        # f"Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz": f"{ENSEMBL_FTP_BASE}release-{release}/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz",
        # f"Homo_sapiens.GRCh38.{release}.gtf.gz": f"{ENSEMBL_FTP_BASE}release-{release}/gtf/homo_sapiens/Homo_sapiens.GRCh38.{release}.gtf.gz"
    }

    target_dir = os.path.join(DATA_DIR, "ensemblData")
    os.makedirs(target_dir, exist_ok=True)

    extracted_files = []

    for filename, url in urls.items():
        dest = os.path.join(target_dir, filename)
        extracted_dest = dest.rstrip('.gz')
        if os.path.exists(extracted_dest):
            print(f"Extracted file already exists: {extracted_dest}")
            extracted_files.append(extracted_dest)
            continue
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(dest, 'wb') as f, tqdm(total=int(r.headers.get('content-length', 0)), unit='B', unit_scale=True) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bar.update(len(chunk))
            print(f"Downloaded: {filename}")

            # --- EXTRACT and DELETE .gz file ---
            extracted = extract_and_delete_gzip(dest)
            if extracted:
                extracted_files.append(extracted)

                # --- MODIFY FASTA HEADER if it's the primary assembly ---
                if "primary_assembly.fa" in extracted:
                    add_chr_prefix_to_fasta(extracted)

        except Exception as e:
            print(f"Failed to download {filename}: {e}")

    # --- SAVE extracted filenames for reference ---
    if extracted_files:
        reference_file = os.path.join(target_dir, "extracted_files.txt")
        with open(reference_file, 'w') as ref:
            for f in extracted_files:
                ref.write(f + '\n')
        print(f"Saved extracted file list to: {reference_file}")
