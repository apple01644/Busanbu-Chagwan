
from requests import get, post
from bs4 import BeautifulSoup as bs
from urllib import parse
import base64
import json
from time import time

class Band:
    urls = {
        'band' : "https://openapi.band.us/v2.1/bands",
        "posts" : "https://openapi.band.us/v2/band/posts"
    }
    def __init__(self):
        self.key = json.load(open('band_api.json','r'))
        self.acs_token = {"access_token" : self.key['access_token']}
        self.band = self.getBand()
        self.time = 0
        self.timer()

    def timer(self):
        result = self.time
        self.time = int(time() * 1000)
        return result

    def getBand(self):
        param = self.acs_token
        band = get(self.urls['band'], params=param).text
        band_key = json.loads(band)
        return band_key['result_data']['bands'][0]['band_key']

    def getPost(self):
        band_key = self.band
        param = self.acs_token
        param['band_key'] = band_key
        param['locale'] = "ko_KR"
        posts = get(self.urls['posts'], params=param).text

        posts = json.loads(posts)
        _time = self.timer()

        return [x for x in posts['result_data']['items'] if x["created_at"] >= _time]
        


if __name__ == "__main__":
    a = Band()
    #print(a.getPost())