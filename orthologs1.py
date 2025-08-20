from config.settings import HUMAN_ORTHO_URL
from utils.dwnld import download_file

def download_orthologs():
    return download_file(HUMAN_ORTHO_URL, "human_orthos.txt", "orthologs")
