import os.path
import signal
from concurrent.futures import ThreadPoolExecutor
from functools import partial
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
        progress.console.log(f"Requesting {url}")
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

        progress.console.log(f"Downloaded {path}")

    def download(self, urls: list[str], dest_dir: str):
        """Download multuple files to the given directory."""

        with progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for url in urls:
                    filename = url.split("/")[-1]
                    dest_path = os.path.join(dest_dir, filename)
                    task_id = progress.add_task(
                        "download", filename=filename, start=False)
                    pool.submit(self.copy_url, task_id, url, dest_path)
