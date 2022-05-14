import abc


class DownloaderBase(metaclass=abc.ABCMeta):
    "Base downloader class, needs to be extended"

    @abc.abstractmethod
    def download(self, compared: tuple[dict[str, dict[str, int]], int], dest_dir: str) -> None:
        raise NotImplemented

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplemented
