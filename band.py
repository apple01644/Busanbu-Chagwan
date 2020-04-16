import json
import time
import requests as req


class Band:
    urls = {
        'band': 'https://openapi.band.us/v2.1/bands',
        'posts': 'https://openapi.band.us/v2/band/posts'
    }

    def __init__(self):
        self.key = json.load(open('band_api.json', 'r'))
        self.param_for_get_band = {'access_token': self.key['access_token']}
        self.param_for_get_post = {'access_token': self.key['access_token'],
                                   'band_key': 'AADe-67DagLFl4xgYFYmMm0r',
                                   'locale': 'ko_KR'}
        self.last_refresh_time = 0
        self.get_post()

    def get_post(self):
        posts = json.loads(req.get(self.urls['posts'], params=self.param_for_get_post).text)
        #print(posts)
        assert posts["result_code"] == 1

        result = [item for item in posts['result_data']['items'] if item['created_at'] > self.last_refresh_time]
        self.last_refresh_time = max([item['created_at'] for item in result] + [self.last_refresh_time])
        return result


band = Band()

if __name__ == '__main__':
    print(band.get_post())
