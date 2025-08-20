import os, gzip, shutil, requests
from pyliftover import LiftOver
from config.settings import DATA_DIR

CHAIN_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/danRer10/liftOver/danRer10ToDanRer11.over.chain.gz"
CHAIN_GZ = os.path.join(DATA_DIR, "liftover.chain.gz")
CHAIN_FILE = os.path.join(DATA_DIR, "liftover.chain")
INPUT_BED = os.path.join(DATA_DIR, "enhanceratlas", "dr.bed")
OUTPUT_BED = os.path.join(DATA_DIR, "output_lifted.bed")
UNMAPPED_LOG = os.path.join(DATA_DIR, "unmapped.txt")
 
def run():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CHAIN_FILE):
        with requests.get(CHAIN_URL, stream=True) as r:
            with open(CHAIN_GZ, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        with gzip.open(CHAIN_GZ, 'rb') as f_in, open(CHAIN_FILE, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    lo = LiftOver(CHAIN_FILE)

    with open(INPUT_BED, 'r') as infile, \
         open(OUTPUT_BED, 'w') as out, \
         open(UNMAPPED_LOG, 'w') as unmapped:
        for line in infile:
            if line.startswith("#") or line.strip() == "": continue
            fields = line.strip().split('\t')
            if len(fields) < 3: continue
            chrom, start, end = fields[0], int(fields[1]), int(fields[2])
            lifted_start = lo.convert_coordinate(chrom, start)
            lifted_end = lo.convert_coordinate(chrom, end-1)
            if lifted_start and lifted_end and lifted_start[0][0] == lifted_end[0][0]:
                new_chrom = lifted_start[0][0]
                new_start = int(lifted_start[0][1])
                new_end = int(lifted_end[0][1]) + 1
                out.write('\t'.join([new_chrom, str(new_start), str(new_end)] + fields[3:]) + '\n')
            else:
                unmapped.write(line)
    print("Liftover complete. Output has been generated.")
