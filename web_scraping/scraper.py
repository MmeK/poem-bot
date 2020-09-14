from urllib.request import urlopen
from bs4 import BeautifulSoup


def main():
    print(article())


def article():
    url = "https://ganjoor.net/hafez/ghazal/sh1/"
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    poem = soup.find_all("article")[0].text.strip().split('\n')
    del poem[1:5]
    return poem


def hafez():
    url = "https://ganjoor.net/hafez/ghazal/sh1/"
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    firsts = map(lambda x: str(x.text), soup.find_all("div", class_='m1'))
    seconds = map(lambda x: str(x.text), soup.find_all("div", class_='m2'))
    beits = list(zip(firsts, seconds))
    return beits


if __name__ == "__main__":
    main()
