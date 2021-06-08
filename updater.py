import requests
import hashlib
import os
import json
import pathlib
from clint.textui import progress


class Mode():
    URL = 1
    FILE = 2


class Updater():
    """
    Main class for updating your project
    
    Args:
        path (os.PathLike): Directory, from which is the hashtable generated
    """

    def __init__(self, path: os.PathLike):
        self.path = path # Starting point
        self.loaded_hashtable = None
        self.generated_hashtable = None

    def create_hash(self, filename: os.PathLike) -> str:
        """Create MD5 hash of file

        Args:
            filename (os.PathLike): File, that will be hashed

        Returns:
            str: MD5 hash
        """        

        data = open(filename, "rb").read()
        return hashlib.md5(data).hexdigest()

    def load_hashtable(self, mode: Mode, target: str) -> dict:
        """Load JSON hashtable as dictionary

        Args:
            mode (Mode): Type of hashtable (File, url)
            target (str): Path to hashtable

        Returns:
            dict: loaded hashtable
        """        

        if mode == Mode.URL:
            table = json.loads(requests.get(
                target, allow_redirects=True).content)

        else:
            with open(target, "r", encoding="utf-8") as f:
                table = json.load(f)

        return dict(table)

    def dump_hashtable(self, hashtable: os.PathLike = "./hashtable.tmp", exclude: list = None) -> os.PathLike:
        """Create new hashtable and dump it into file

        Args:
            hashtable (os.PathLike, optional): Where should the result be dumped. Defaults to "./hashtable.tmp".
            exclude (list, optional): files or folders, that will be excluded. Defaults to None.

        Returns:
            os.PathLike: Absolute path to the generated hashtable
        """        

        if exclude == None:
            exclude = []

        _new = []
        for item in exclude:
            _new.append(os.path.normpath(item))
        exclude = _new

        generated = self.generate_hashtable(exclude)

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

        for dirpath, _, files in os.walk(self.path):
            if files != []:
                
                for file in files:
                    path = os.path.normpath(os.path.join(dirpath, file))
                    if not path in exclude:
                        generated[path] = {
                            "hash": self.create_hash(path),
                            "size": os.path.getsize(path)
                        }

        return dict(generated)

    def compare(self, mode: Mode, target: str, rebase: bool = False) -> list:
        """Generate hashtable and compare it to local file or mirror\n

        TODO: Implement rebase

        Args:
            mode (Mode): Type of hashtable (file, URL)
            target (str): Path or URL to hashtable
            rebase (bool, optional): Reset directory to state described by hashtable. Defaults to False.

        Returns:
            list: Absent or modified files
        """        

        self.generated_hashtable = self.generate_hashtable(exclude=list())
        self.loaded_hashtable = self.load_hashtable(mode, target)

        diff = {}
        for k in self.loaded_hashtable:
            if k in self.generated_hashtable and self.loaded_hashtable[k] != self.generated_hashtable[k]:
                diff[pathlib.Path(k).as_posix()] = self.loaded_hashtable[k]
            if not k in self.generated_hashtable:
                diff[pathlib.Path(k).as_posix()] = self.loaded_hashtable[k]

        

        return list(diff.keys())

    def download(self, mirror: str, mode: Mode, target: str, rebase: bool = False):
        """Download files based on difference in hashtables or rebase(validate) all files

        Args:
            mirror (str): root URL for retrieving files
            mode (Mode): Type of hashtable (file, URL)
            target (str): Path or URL to hashtable
            rebase (bool, optional): Reset directory to state described by hashtable. Defaults to False.
        """        
        
        different = self.compare(mode, target, rebase)

        mirror = mirror if mirror[-1] == "/" else mirror + "/"

        for item in different:
            with open(item, "wb") as f:
                response = requests.get(mirror+item, stream=True)
                total_length = int(response.headers.get('content-length'))
                for chunk in progress.bar(response.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1, label=item): 
                    if chunk:
                        f.write(chunk)
                        f.flush()
