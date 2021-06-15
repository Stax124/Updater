import requests
import hashlib
import os
import json
import pathlib
from tqdm import tqdm
from downloader import download_file

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
        
        os.chdir(self.path)

    def human_readable(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def create_hash(self, filename: os.PathLike) -> str:
        """Create MD5 hash of file

        Args:
            filename (os.PathLike): File, that will be hashed

        Returns:
            str: MD5 hash
        """

        sha = hashlib.sha256()
        
        with open(filename, 'rb') as f:
            with tqdm(total=os.stat(filename).st_size, unit='B',
                  unit_scale=True, unit_divisor=1024,
                  desc="Hashing "+filename, ascii=False, leave=False) as pbar:
                while True:
                    chunk = f.read(1000 * 1000)  # 1MB so that memory is not exhausted
                    if not chunk:
                        break
                    sha.update(chunk)
                    pbar.update(1000*1000)
                
        return sha.hexdigest()

    def load_hashtable(self, url: str) -> dict:
        """Load URL as dictionary

        Args:
            url (str): Path to hashtable

        Returns:
            dict: loaded hashtable
        """        

        table = json.loads(requests.get(
            url, allow_redirects=True).content)

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

        excluded_directories = []
        excluded_files = []
        for item in exclude:
            if os.path.isdir(item):
                excluded_directories.append(item)
            elif os.path.isfile(item):
                excluded_files.append(item)

        for dirpath, _, files in os.walk(self.path):
            if os.path.normpath(dirpath) in excluded_directories:
                continue
            
            if files != []:
                
                for file in files:
                    path = os.path.normpath(os.path.join(dirpath, file))
                    if not path in excluded_files:
                        generated[path] = {
                            "hash": self.create_hash(path),
                            "size": os.path.getsize(path)
                        }

        return dict(generated)

    def compare(self, url: str) -> list:
        """Generate hashtable and compare it to local file or mirror\n

        Args:
            mode (Mode): Type of hashtable (file, URL)
            url (str): Path or URL to hashtable

        Returns:
            dict: Absent or modified files
            int: Size of files that needs to be downloaded
        """        

        self.generated_hashtable = self.generate_hashtable(exclude=list())
        self.loaded_hashtable = self.load_hashtable(url)

        diff = {}
        size = 0
        for k in self.loaded_hashtable:
            if k in self.generated_hashtable and self.loaded_hashtable[k] != self.generated_hashtable[k]:
                diff[pathlib.Path(k).as_posix()] = self.loaded_hashtable[k]
                size += self.loaded_hashtable[k]["size"]
            if not k in self.generated_hashtable:
                diff[pathlib.Path(k).as_posix()] = self.loaded_hashtable[k]
                size += self.loaded_hashtable[k]["size"]

        return (diff, size)

    def download(self, mirror: str, hashtable: str, prompt_user: bool = True):
        def execute():
            for item in compared.keys():
                download_file(mirror+item, self.path, compared[item]["hash"])
        
        if not mirror[-1] == "/": mirror+="/"
        
        compared, size = self.compare(hashtable)
        
        if size == 0:
            print("All files validated, nothing to download")
            return
        
        if prompt_user:
            try:
                response = input(f"Total size: {self.human_readable(size)}\nDo you want to start download ? (y/n): ")
                
                if response == "" or response.lower() == "y":
                    execute()
                else:
                    raise KeyboardInterrupt
            except KeyboardInterrupt:
                print("\nCanceled by user, quitting")
        else:
            execute()
