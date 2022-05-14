import os.path
import signal
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import PathLike
from pathlib import Path
from threading import Event
from urllib.request import urlopen

from rich.progress import (BarColumn, DownloadColumn, Progress, TaskID,
                           TextColumn, TimeRemainingColumn,
                           TransferSpeedColumn)

from .downloader_template import DownloaderBase

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


class UrllibDownloader(DownloaderBase):
    @property
    def name(self) -> str:
        return "urllib_downloader"

    def handle_sigint(self, signum, frame):
        self.done_event.set()

    def __init__(self) -> None:
        self.done_event = Event()
        signal.signal(signal.SIGINT, self.handle_sigint)

    def copy_url(self, task_id: TaskID, url: str, path: str) -> None:
        """Copy data from a url to a local file."""
        response = urlopen(url)

        # This will break if the response doesn't contain content length
        progress.update(task_id, total=int(response.info()["Content-length"]))

        with open(path, "wb") as dest_file:
            progress.start_task(task_id)
            for data in iter(partial(response.read, 32768), b""):
                dest_file.write(data)
                progress.update(task_id, advance=len(data))
                if self.done_event.is_set():
                    return

    def download(self, compared: dict[str, dict[str, int]], mirror: str,  dest_dir: str | PathLike):
        """Download multuple files to the given directory."""

        urls = [(mirror+i, i) for i in compared.keys()]

        for url, file in urls:
            dest_path = os.path.join(dest_dir, file)
            file = Path(dest_path)
            filedir = Path(file.parents[0]).absolute()
            Path(filedir).mkdir(parents=True, exist_ok=True)

        with progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for url, file in urls:
                    dest_path = os.path.join(dest_dir, file)
                    task_id = progress.add_task(
                        "Downloading", filename=file, start=False)
                    pool.submit(self.copy_url, task_id, url, dest_path)
