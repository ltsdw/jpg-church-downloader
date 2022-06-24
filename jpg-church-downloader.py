from urllib.request import Request, urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup, ResultSet
from os import path, mkdir, getcwd, chdir
from sys import exit
from typing import Any, List
from requests import get
from urllib.request import Request, urlopen


_UrlopenRet: Any = Any


class Main:
    def __init__(self, url: str) -> None:
        self.url: str = url


    def createDir(self) -> None:
        req: Request = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            page: _UrlopenRet = urlopen(req).read()
        except URLError:
            exit('verify the connection with the internet!')


        soup: BeautifulSoup = BeautifulSoup(page, 'html.parser')

        dir_name: ResultSet = soup.find("h1", class_="text-overflow-ellipsis")


        current_dir: str = getcwd()
        filepath: str = path.join(current_dir, dir_name.get_text().replace("/", "-"))

        try:
            mkdir(path.join(filepath))
        # if the directory already exist is safe to do nothing
        except FileExistsError:
            pass

        chdir(filepath)


    def downloadImages(self) -> None:
        req: Request = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})


        try:
            page: _UrlopenRet = urlopen(req).read()
        except URLError:
            exit('verify the connection with the internet!')


        soup: BeautifulSoup = BeautifulSoup(page, 'html.parser')

        images_urls: ResultSet = soup.find_all("div", class_="list-item-image fixed-size")

        url: List[str]
        concat_url: str

        for i in images_urls:
            file = i.find("img", alt=True)["alt"]
            
            try:
                url = i.find("img", alt=True)["src"].split("/")[:-1]

                concat_url = "https://" + "".join([i + "/" for i in url[2:]]) + file
            except IndexError:
                if concat_url:
                    print(f"Something went wronge when parsing the url {concat_url}")
                else:
                    print(f"Empty url internally parsed: {url}")

                exit(-1)

            if not file:
                print("Empty filename: Error when parsing filename")
                exit(-1)


            try:
                img_data = get(concat_url).content

                with open(file, 'wb') as handler:
                    handler.write(img_data)
            except:
                pass



if __name__ == '__main__':
    print('Starting, please wait...')

    try:
        from os import environ
        from sys import argv


        url: str


        try:
            url = argv[1]

            if not url.split('/')[-2] == "a":
                print(f"the url is propably not an album {url}")
                exit(-1)

        except IndexError:
            print("specify an url, like: ./jpg-church-downloader.py https://jpg.church/a/albumname")
            exit(-1)


        m: Main = Main(url=url)
        m.createDir()
        m.downloadImages()

    except KeyboardInterrupt:
        exit(1)

