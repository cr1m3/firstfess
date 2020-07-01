from tweepy import OAuthHandler, API
from autofess import config


class AutoFess:
    def __init__(self):
        auth = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
        auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
        self.api = API(auth)

    def start(self):
        me = self.api.me()
        print(f"AutoFess started on @{me.screen_name}. Hi.")

    def get_api(self):
        return self.api
