import hashlib
import json
import logging as console
import os
import pathlib
from pathlib import Path
from typing import Union

import requests
from tqdm import tqdm

from core.requests_downloader import RequestsDownloader


class Updater():
    """
    Main class for updating your project

    Args:
        path (os.PathLike): Directory, from which is the hashtable generated
    """

    def __init__(self, path: str | os.PathLike = "."):  # type: ignore
        self.path = path
        self.loaded_hashtable = dict[str, dict[str, int]]()
        self.generated_hashtable = dict[str, dict[str, int]]()

    def human_readable(self, num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def create_hash(self, filename: Union[str, os.PathLike]) -> str:
        """Create MD5 hash of file

        Args:
            filename (os.PathLike): File, that will be hashed

        Returns:
            str: MD5 hash
        """

        console.debug(f"Hashing: {filename}")

        sha = hashlib.sha256()

        try:
            with open(filename, 'rb') as f:
                with tqdm(total=os.stat(filename).st_size, unit='B', leave=False,
                          unit_scale=True, unit_divisor=1024,
                          desc="Hashing "+filename.__str__() if len(filename.__str__()) < 20 else filename.__str__()[:20] + "...", ascii=False, colour="green") as progressbar:
                    while True:
                        # 1MB so that memory is not exhausted
                        chunk = f.read(1000 * 1000)
                        if not chunk:
                            break
                        sha.update(chunk)
                        progressbar.update(1000*1000)
        except FileNotFoundError:
            console.error(f"File not found: {filename}")

        return sha.hexdigest()

    def load_hashtable(self, url: str) -> dict[str, dict]:
        """Load URL as dictionary

        Args:
            url (str): Path to hashtable

        Returns:
            dict: loaded hashtable
        """

        console.debug(f"Loading hashtable from {url}")

        table = json.loads(requests.get(
            url, allow_redirects=True).content)

        return dict(table)

    def exclude(self, exclude: list[str]) -> tuple:
        excluded_directories, excluded_files = [], []

        for item in exclude:
            console.debug(f"Exclude - processing: {item}")
            if os.path.isdir(item):
                console.debug(f"Exclude - processing: {item} is directory")
                excluded_directories.append(item)
            elif os.path.isfile(item):
                console.debug(f"Exclude - processing: {item} is file")
                excluded_files.append(Path(item).as_posix())

        console.debug(f"Excluded directories: {excluded_directories}")
        console.debug(f"Excluded files: {excluded_files}")

        return excluded_directories, excluded_files

    def dump_hashtable(self, hashtable: os.PathLike, exclude: list[str] | None = None) -> os.PathLike:
        """Create new hashtable and dump it into file

        Args:
            hashtable (os.PathLike, optional): Where should the result be dumped. Defaults to "./hashtable.tmp".
            exclude (list, optional): files or folders, that will be excluded. Defaults to None.

        Returns:
            os.PathLike: Absolute path to the generated hashtable
        """
        _exclude: list[str] = []

        if exclude == None:
            _exclude = []
        else:
            _exclude = exclude  # type: ignore

        _new = []
        for item in _exclude:
            _new.append(os.path.normpath(item))
        _exclude = _new

        generated = self.generate_hashtable(_exclude)

        console.debug(f"Dumping hashtable to {hashtable}")
        with open(hashtable, "w", encoding="utf-8") as ht:
            json.dump(generated, ht, ensure_ascii=False, indent=4)

        return os.path.abspath(hashtable)

    def generate_hashtable(self, exclude: list) -> dict:
        """Generate hashtable of directory parsed to main class

        Args:
            exclude (list): files or folders, that will be excluded

        Returns:
            >>> "filename": {
            >>>     'hash': 'MD5 hash'
            >>>     'size': 'size of file'
            >>> }
        """

        generated = {}

        excluded_directories, excluded_files = self.exclude(exclude)

        for dirpath, _, files in os.walk(self.path):
            console.debug(
                f"Formated: {os.path.normpath(dirpath).split(os.path.sep)[0]}; Excluded directories: {excluded_directories}; Skipping: {os.path.normpath(dirpath).split(os.path.sep)[0] in excluded_directories}")
            if os.path.normpath(dirpath).split(os.path.sep)[0] in excluded_directories:
                continue

            if files != []:

                for file in files:
                    path = Path(os.path.normpath(
                        os.path.join(dirpath, file))).as_posix()
                    if not path in excluded_files:
                        generated[path] = {
                            "hash": self.create_hash(path),
                            "size": os.path.getsize(path)
                        }

        return dict(generated)

    def generate_hashtable_from_remote(self, remote_hashtable: dict) -> dict:
        """Generate hashtable of directory parsed to main class

        Args:
            remote_hashtable (dict): Only files in remote_hashtable will be hashed locally

        Returns:
            >>> "filename": {
            >>>     'hash': 'MD5 hash'
            >>>     'size': 'size of file'
            >>> }
        """

        generated = {}

        for file in [i for i in remote_hashtable]:
            try:
                path = Path(os.path.normpath(
                    os.path.join(".", file))).as_posix()
                generated[path] = {
                    "hash": self.create_hash(path),
                    "size": os.path.getsize(path)
                }
            except FileNotFoundError:
                pass

        return dict(generated)

    def compare(self, url: str, hash_all: bool = False) -> tuple[dict[str, dict[str, int]], int]:
        """Generate hashtable and compare it to local file or mirror\n

        Args:
            url (str): Path or URL to hashtable
            hash_all (bool, optional): If True, all files will be hashed. Defaults to False.

        Returns:
            dict: Absent or modified files
            int: Size of files that needs to be downloaded
        """

        self.loaded_hashtable = self.load_hashtable(url)
        self.generated_hashtable = self.generate_hashtable(
            exclude=list()) if hash_all else self.generate_hashtable_from_remote(self.loaded_hashtable)

        diff: dict[str, dict[str, int]] = {}
        size = 0
        for k in self.loaded_hashtable:
            if k in self.generated_hashtable and self.loaded_hashtable[k] != self.generated_hashtable[k]:
                diff[pathlib.Path(k).as_posix()] = self.loaded_hashtable[k]
                size += self.loaded_hashtable[k]["size"]
            if not k in self.generated_hashtable:
                diff[pathlib.Path(k).as_posix()] = self.loaded_hashtable[k]
                size += self.loaded_hashtable[k]["size"]

        return (diff, size)

    def reset_head(self) -> None:
        "Removes all files that are not present in the remote hashtable"

        # get list of all files that are in generated_hashtable but not in loaded_hashtable
        filtered_list = [
            i for i in self.generated_hashtable if i not in self.loaded_hashtable]

        console.info(f"Removing {filtered_list} files")
        
        console.info(f"Generated: {self.generated_hashtable}")
        console.info(f"Loaded: {self.loaded_hashtable}")

        # remove all files that are in filtered_list
        for file in filtered_list:
            os.remove(file)

        console.info(
            f"{len(filtered_list)} files were reset to state of remote repository")

    def run(self, mirror: str, hashtable: str, prompt_user: bool = True, reset_to_remote: bool = False):
        def download_all():
            """Download all missing files"""

            # for item in compared.keys():
            #     download_file(mirror, item, self.path,
            #                   compared[item]["hash"])  # type: ignore

            downloader = RequestsDownloader()
            downloader.download(compared, mirror, self.path)

        compared, size = self.compare(hashtable, hash_all=reset_to_remote)

        if reset_to_remote:
            self.reset_head()

        if size == 0:
            console.info("All files validated, nothing to download")
            return

        if prompt_user:
            try:
                response = input(
                    f"Total size: {self.human_readable(size)}\nDo you want to start download ? (y/n): ").strip().lower()

                if response == "y":
                    download_all()
                else:
                    raise KeyboardInterrupt
            except KeyboardInterrupt:
                console.warning("\nCancelled by user, quitting")
        else:
            download_all()
