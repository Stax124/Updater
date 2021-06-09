import hashlib
import requests

from pathlib import Path
from tqdm import tqdm


def downloader(url: str, download_folder: str, resume_byte_pos: int = None):
    """Download url in ``URLS[position]`` to disk with possible resumption."""
    # Get size of file
    DOWNLOAD_FOLDER = Path(download_folder)
    r = requests.head(url)
    file_size = int(r.headers.get('content-length', 0))

    # Append information to resume download at specific byte position
    # to header
    resume_header = ({'Range': f'bytes={resume_byte_pos}-'}
                     if resume_byte_pos else None)

    # Establish connection
    r = requests.get(url, stream=True, headers=resume_header)

    # Set configuration
    block_size = 1024
    initial_pos = resume_byte_pos if resume_byte_pos else 0
    mode = 'ab' if resume_byte_pos else 'wb'
    file = DOWNLOAD_FOLDER / url.split('/')[-1]

    with open(file, mode) as f:
        with tqdm(total=file_size, unit='B',
                  unit_scale=True, unit_divisor=1024,
                  desc=file.name, initial=initial_pos,
                  ascii=True, miniters=1) as pbar:
            for chunk in r.iter_content(32 * block_size):
                f.write(chunk)
                pbar.update(len(chunk))


def download_file(url: str, download_folder: str, targeted_hash: str) -> None:
    """Execute the correct download operation.
    Depending on the size of the file online and offline, resume the
    download if the file offline is smaller than online.
    """
    # Establish connection to header of file
    DOWNLOAD_FOLDER = Path(download_folder)
    r = requests.head(url)

    # Get filesize of online and offline file
    file_size_online = int(r.headers.get('content-length', 0))
    file = DOWNLOAD_FOLDER / url.split('/')[-1]

    if file.exists():
        file_size_offline = file.stat().st_size

        if file_size_online > file_size_offline:
            print(f'{file} is incomplete. Resume download.')
            downloader(url, download_folder, file_size_offline)
        else:
            downloader(url, download_folder)
            pass
    else:
        downloader(url, download_folder)
    
    if not validate_file(file, targeted_hash):
        raise AssertionError("File is corrupted, restart updater")


def validate_file(file: str, hash: str) -> None:
    """Validate a given file with its hash.
    The downloaded file is hashed and compared to a pre-registered
    has value to validate the download procedure.
    """

    sha = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            chunk = f.read(1000 * 1000)  # 1MB so that memory is not exhausted
            if not chunk:
                break
            sha.update(chunk)
    
    if not sha.hexdigest() == hash: return False
    else: return True