import requests
import shutil
import json
import time
import os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pprint import pprint


def feed_key(cookies):
    url = "https://pikabu.ru/liked"
    body = requests.get(url, cookies=cookies).text
    soup = BeautifulSoup(body, "html.parser")
    feed_key = json.loads(
        soup.select('script.app__config[data-entry="feed-filter"]')[0].text
    )["feedKey"]
    return feed_key


def liked():
    with open("cookies.json") as f:
        cookies = json.load(f)
    s = requests.session()
    # s.headers.update(
    #     {
    #         "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    #         "origin": "https://pikabu.ru",
    #         "referer": "https://pikabu.ru",
    #         "accept": "*/*",
    #         # "accept-encoding": "gzip, deflate, br, zstd",
    #         "priority": "u=4",
    #         "sec-fetch-dest": "empty",
    #         "sec-fetch-mode": "cors",
    #         "sec-fetch-site": "same-site",
    #         "TE": "trailers",
    #     }
    # )
    for k in cookies:
        s.cookies.set(k, cookies[k])

    # pprint(s.cookies.get_dict("pikabu.ru"))

    key = feed_key(cookies)
    result = []
    i = 0
    while True:
        i += 1
        req = s.get(
            "https://pikabu.ru/ajax/liked?key={feed_key}&page={page}&_={time}".format(
                feed_key=key, page=i, time=round(time.time() * 1000)
            )
        )
        text = req.text
        page = json.loads(text)

        stories = page["data"]["stories"]
        if len(stories) == 0:
            break

        for story in stories:
            id = story["id"]
            print("id: {}".format(id))
            html = story["html"]
            soup = BeautifulSoup(html, "html.parser")
            for img in soup.select("[data-large-image]"):
                offset = img.get("data-scrambler-offset")
                url = img.get("data-large-image")
                parsed_url = urlparse(url)
                path = parsed_url.path
                filename = os.path.basename(path)
                print(url)
                r = s.get(url, stream=True)
                fn1 = "raw/{}".format(filename)
                fn2 = "images/{}".format(filename)
                with open(fn1, "wb") as out:
                    shutil.copyfileobj(r.raw, out)
                os.system("./descramble.js {} {} {}".format(fn1, offset, fn2))

        # return
    return result
