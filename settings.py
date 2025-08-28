import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


ENSEMBL_FTP_BASE = "https://ftp.ensembl.org/pub/"
COSMIC_API_BASE = "https://cancer.sanger.ac.uk/api/mono/products/v1/downloads/scripted"
COSMIC_FILE_PATH = "grch38/cosmic/v101/Cosmic_CancerGeneCensus_Tsv_v101_GRCh38.tar"
MIRGENE_URL = "https://mirgenedb.org/static/data/dre/dre-all.bed"
HUMAN_ORTHO_URL = "https://zfin.org/downloads/human_orthos.txt"
ENHANCERATLAS_URL = "http://www.enhanceratlas.org/data/download/species_enh_bed.tar.gz"

LNC_RNA_URL = "https://www.biochen.org/zflnc/static/download/ZFLNC_lncRNA.gtf.zip"
T_RNA_URL = "https://gtrnadb.ucsc.edu/genomes/eukaryota/Dreri11/danRer11-tRNAs.tar.gz"

HTTP_STATUS_CODES = {
    200: "OK - The request was successful.",
    301: "Moved Permanently - The resource has been moved to a new location.",
    302: "Found - The resource was found but temporarily moved.",
    400: "Bad Request - The request was invalid or malformed.",
    401: "Unauthorized - Authentication is required but failed or not provided.",
    403: "Forbidden - The server understood the request but refuses to authorize it.",
    404: "Not Found - The requested resource was not found on the server.",
    500: "Internal Server Error - The server encountered an unexpected condition. Please try again later...",
    502: "Bad Gateway - The server received an invalid response from another server. Please try again later...",
    503: "Service Unavailable - The server is not ready to handle the request. Please try again later...",
    504: "Gateway Timeout - The server did not receive a timely response. Please try again later..."
}

DATA_DIR = "data"