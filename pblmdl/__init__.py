import requests
import json
import time
import pickle
import shutil
from pblmdl import descrambler
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path


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
    for k in cookies:
        s.cookies.set(k, cookies[k])

    key = feed_key(cookies)

    seen = set()
    try:
        with open("seen", "rb") as f:
            seen = pickle.load(f)
    except FileNotFoundError:
        print("'seen' not found")

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
            html = story["html"]
            if id in seen:
                print("story [{}] already seen, finishing".format(id))
                save_seen(seen)
                return
            soup = BeautifulSoup(html, "html.parser")
            story_url = soup.select("a.story__title-link")[0].get("href")
            print("story [{}] {}".format(id, story_url))
            if len(soup.select("[data-tag='NSFW']")) == 0:
                print("story is SFW, skipping")
                continue
            for img in soup.select("[data-large-image]"):
                url = img.get("data-large-image")
                offset = img.get("data-scrambler-offset")
                if offset is not None:
                    offset = int(offset)
                else:
                    print("image at {} is not scrambled".format(url))
                parsed_url = urlparse(url)
                path = parsed_url.path
                filename = (
                    path.replace("/post_img/big/", "", 1)
                    .replace("/post_img/", "", 1)
                    .replace("/", "-")
                )
                print("img: {}".format(url))
                output_filename = Path("pikabu/{}".format(filename))
                descrambler.ImageDescrambler.descramble_url(
                    url, offset, output_filename
                )
            for vid in soup.select("div.player"):
                # return vid
                # url = vid.get("data-webm")
                url = vid.get("data-source")
                if url is None:
                    print("didn't find video url at story {}".format(id))
                    continue
                url = url + ".mp4"
                print("vid: {}".format(url))
                parsed_url = urlparse(url)
                path = parsed_url.path
                filename = (
                    path.replace("/video/", "", 1)
                    .replace("/post_img/", "", 1)
                    .replace("/", "-")
                )
                response = s.get(url, stream=True)
                with open("pikabu/{}".format(filename), "wb") as out:
                    shutil.copyfileobj(response.raw, out)
            seen.add(id)

    save_seen(seen)


def save_seen(seen):
    with open("seen", "wb") as f:
        pickle.dump(seen, f)
