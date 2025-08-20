import os, requests
from config.settings import MIRGENE_URL, DATA_DIR, HTTP_STATUS_CODES
from tqdm import tqdm

def download():
    target_dir = os.path.join(DATA_DIR, "mirgene")
    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, "dre-all.bed")

    # Checkingg if thee file already exists
    if os.path.exists(filepath):
        print(f"miRGene data already downloaded at {filepath}")
        return filepath

    try:
        response = requests.get(MIRGENE_URL, stream=True)
        status_code = response.status_code
        if status_code != 200:
            msg = HTTP_STATUS_CODES.get(status_code, f"Unexpected status code {status_code}")
            raise Exception(f"❌ Failed to download miRGene data: {msg}")
    except Exception as e:
        print(str(e))
        return None

    # Savingg the filee
    total_size = int(response.headers.get('content-length', 0))
    with open(filepath, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    print("miRGene data downloaded.")
    return filepath


# mirgene.py
# import os, requests, time
# from config.settings import MIRGENE_URL, DATA_DIR, HTTP_STATUS_CODES
# from tqdm import tqdm
# from utils.logger import log_download_task

# @log_download_task(script_name="mirgene.py")
# def download():
#     target_dir = os.path.join(DATA_DIR, "mirgene")
#     os.makedirs(target_dir, exist_ok=True)
#     filename = "dre-all.bed"
#     filepath = os.path.join(target_dir, filename)
#     start = time.time()

#     # Skip if exists
#     if os.path.exists(filepath):
#         print(f"miRGene data already downloaded at {filepath}")
#         return filepath, [{
#             "filename": filename,
#             "source_url": MIRGENE_URL,
#             "file_type": "bed",
#             "release_version": None,
#             "downloaded": False,
#             "extracted": False,
#             "deleted": False,
#             "modified": False,
#             "file_size": os.path.getsize(filepath),
#             "duration_sec": 0,
#             "status": "skipped",
#             "error_message": None
#         }]

#     try:
#         response = requests.get(MIRGENE_URL, stream=True)
#         if response.status_code != 200:
#             msg = HTTP_STATUS_CODES.get(response.status_code, f"Unexpected status code {response.status_code}")
#             raise Exception(msg)
#         total_size = int(response.headers.get('content-length', 0))
#         with open(filepath, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)
#                 bar.update(len(chunk))
#         file_size = os.path.getsize(filepath)
#         return [{
#             "filename": filename,
#             "source_url": MIRGENE_URL,
#             "file_type": "bed",
#             "release_version": None,
#             "downloaded": True,
#             "extracted": False,
#             "deleted": False,
#             "modified": False,
#             "file_size": file_size,
#             "duration_sec": round(time.time() - start, 2),
#             "status": "success",
#             "error_message": None
#         }]
#     except Exception as e:
#         return [{
#             "filename": filename,
#             "source_url": MIRGENE_URL,
#             "file_type": "bed",
#             "release_version": None,
#             "downloaded": False,
#             "extracted": False,
#             "deleted": False,
#             "modified": False,
#             "file_size": 0,
#             "duration_sec": round(time.time() - start, 2),
#             "status": "failed",
#             "error_message": str(e)
#         }]
    
#     # Savingg the filee
#     total_size = int(response.headers.get('content-length', 0))
#     with open(filepath, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
#         for chunk in response.iter_content(chunk_size=8192):
#             f.write(chunk)
#             bar.update(len(chunk))

#     print("miRGene data downloaded.")
#     return filepath