import hashlib
import logging as console
import os
from os import PathLike
from pathlib import Path

import requests
from rich.progress import (BarColumn, DownloadColumn, Progress, TextColumn,
                           TimeRemainingColumn, TransferSpeedColumn)

from core.downloader_template import DownloaderBase


class RequestsDownloader(DownloaderBase):
    @property
    def name(self) -> str:
        return "requests_downloader"

    def download(self, compared: dict[str, dict[str, int]], mirror: str,  dest_dir: str | PathLike) -> None:
        "Download files from remote repository."

        for item in compared.keys():
            self.download_file(mirror+item, os.path.join(dest_dir, item),  # type: ignore
                               compared[item]["hash"])  # type: ignore

    def validate_file(self, file: Path, hash: str) -> bool:
        """
        Validate a given file with its hash.
        The downloaded file is hashed and compared to a pre-registered
        has value to validate the download procedure.
        """

        sha = hashlib.sha256()

        with Progress(TextColumn("[bold purple]H: [bold blue]{task.fields[filename]}", justify="right"),
                      BarColumn(bar_width=None),
                      "[progress.percentage]{task.percentage:>3.1f}%",
                      "•",
                      DownloadColumn(),
                      "•",
                      TransferSpeedColumn(),
                      "•",
                      TimeRemainingColumn(),) as progress:
            task = progress.add_task(
                file.name, filename=file.name, total=file.stat().st_size)

            with open(file, 'rb') as f:
                # with tqdm(total=file.stat().st_size, unit='B',
                #         unit_scale=True, unit_divisor=1024,
                #         desc=file.name, ascii=False, leave=False) as progressbar:
                while True:
                    # 1MB so that memory is not exhausted
                    chunk = f.read(1000 * 1000)
                    if not chunk:
                        break
                    sha.update(chunk)
                    progress.update(task, advance=1000)

        if not sha.hexdigest() == hash:
            return False
        else:
            return True

    def download_file(self, url: str, file: Path, verification_hash: str) -> None:
        "Download file from remote repository."

        resume_byte_position = 0

        # Establish connection to header of file
        r = requests.head(url)

        # Get filesize of online and offline file
        file_size = int(r.headers.get('content-length', 0))
        file = Path(file)
        filedir = Path(file.parents[0]).absolute()
        Path(filedir).mkdir(parents=True, exist_ok=True)

        if file.exists():
            file_size_offline = file.stat().st_size

            if file_size > file_size_offline:
                console.info(f'{file} is incomplete. Resuming download.')
                resume_byte_position = file_size_offline

        # Append information to resume download at specific byte position
        # to header
        resume_header = ({'Range': f'bytes={resume_byte_position}-'}
                         if resume_byte_position else None)

        # Establish connection
        r = requests.get(url, stream=True, headers=resume_header)

        # Set configuration
        block_size = 1024
        initial_pos = resume_byte_position if resume_byte_position else 0
        mode = 'ab' if resume_byte_position else 'wb'

        with Progress(TextColumn("[bold green]D: [bold blue]{task.fields[filename]}", justify="right"),
                      BarColumn(bar_width=None),
                      "[progress.percentage]{task.percentage:>3.1f}%",
                      "•",
                      DownloadColumn(),
                      "•",
                      TransferSpeedColumn(),
                      "•",
                      TimeRemainingColumn(),) as progress:
            task = progress.add_task(
                file.name, filename=file.name, total=file_size, completed=initial_pos)

            with open(file, mode) as f:
                # with tqdm(total=file_size, unit='B',
                #           unit_scale=True, unit_divisor=1024,
                #           desc=file.name, initial=initial_pos,
                #           ascii=False, leave=False) as progressbar:
                for chunk in r.iter_content(32 * block_size):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
