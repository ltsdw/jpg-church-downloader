from urllib.request import Request, urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup, ResultSet, Tag, NavigableString
from os import path, mkdir, getcwd, chdir
from sys import exit, stdout, stderr
from typing import Any, List, Generator
from requests import get
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
from platform import system


_UrlopenRet = Any


NEW_LINE: str = "\n"


if system() == "Windows":
    NEW_LINE = "\r\n"


def die(message: str) -> None:
    """
    Display a message of error and exit.
    :param message: message to be displayed.
    :return:
    """


    stderr.write(message + NEW_LINE)
    stderr.flush()

    exit(-1)


class Main:
    def __init__(self, url: str, _max_workers: int = 20) -> None:

        self._page: _UrlopenRet = self._makeRequest(url)
        self._soup: BeautifulSoup = BeautifulSoup(self._page, "html.parser") 

        self._createDir(self._soup)

        self._threadedDownloads(_max_workers)


    def _threadedDownloads(self, max_workers: int) -> None:
        """
        Parallelize the downloads.

        :param max_workers: the max thread number.
        :return:
        """

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for link in self._getLinks(self._soup):
                executor.submit(self._downloadImage, link)


    @staticmethod
    def _makeRequest(url: str) -> _UrlopenRet:
        """
        Return the content of the request. 

        :param page: url to the album.
        :return
        """

        req: Request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            page: _UrlopenRet = urlopen(req).read()

            return page

        except URLError:
            die("Failed to make a page request verify your internet connection!")


    @staticmethod
    def _createDir(soup: BeautifulSoup) -> None:
        """
        creates a directory where the files will be saved if doesn't exist and change to it.

        :param soup: parsed html album's content.
        :return
        """

        dir_name: Tag | NavigableString | None = soup.find("h1", class_="text-overflow-ellipsis")

        if dir_name:
            current_dir: str = getcwd()
            filepath: str = path.join(current_dir, dir_name.get_text().replace("/", "-"))

            try:
                mkdir(path.join(filepath))
            # if the directory already exist is safe to do nothing
            except FileExistsError:
                pass

            chdir(filepath)
        else:
            die(f"Failed to parse a directory name from the {url}")


    @staticmethod
    def _getLinks(soup: BeautifulSoup) -> Generator[str, None, None]:
        """
        Yields each and every image link from the page.

        :param soup: parsed html album's content.
        :return: an generator of type string, the file link. 
        """

        images_urls: ResultSet = soup.find_all("div", class_="list-item-image fixed-size")

        image_url: List[str]
        concat_url: str = ""

        for i in images_urls:
            file: str = i.find("img", alt=True)["alt"]


            try:
                image_url = i.find("img", alt=True)["src"].split("/")[:-1]

                concat_url = "https://" + "".join([i + "/" for i in image_url[2:]]) + file
                
                yield concat_url

            except IndexError:
                die(f"Something went wrong while trying to get link {i}.")


    @staticmethod
    def _downloadImage(url: str, chunk_size: int = 4096) -> None:
        """
        Download the content of the url.

        :param url: url to the image.
        :param chunk_size: the number of bytes it should read into memory.
        :return:
        """

        file: str = url.split("/")[-1]

        if not file:
            print(f"Failed to get a filename for {url}")

            return
       
        with get(url, stream=True) as response_handler:
            if response_handler.status_code in (403, 404, 405, 500):
                print(f"Couldn't download the file from {url}." + NEW_LINE + "Status code: {response_handler.status_code}")
                return
            with open(file, 'wb+') as handler:
                has_size: str | None = response_handler.headers.get('Content-Length')

                total_size: float

                if has_size:
                    total_size = float(has_size)
                else:
                    print(f"{file} has no content.")
                    return
                
                for i, chunk in enumerate(response_handler.iter_content(chunk_size)):
                    progress: float = i * chunk_size / total_size * 100

                    handler.write(chunk)

                    stdout.write(f"\rDownloading {file}: {round(progress, 1)}%")
                    stdout.flush()

                stdout.write(f"\rDownloaded {file}: 100.0%!" + NEW_LINE)
                stdout.flush()


if __name__ == '__main__':
    print('Starting, please wait...')

    try:
        from sys import argv


        try:
            url: str = argv[1]

            if not url.split('/')[-2] == "a":
                die(f"the url is propably not an album {url}")

            Main(url=url)
        except IndexError:
            die("specify an url, like: python jpg-church-downloader.py https://jpg.church/a/albumname")


    except KeyboardInterrupt:
        exit(1)

