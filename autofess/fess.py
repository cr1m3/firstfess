from tweepy import OAuthHandler, Stream, StreamListener, API
from autofess import config

Config = config.Config()
class AutoFess():
    def __init__(self):
        auth = OAuthHandler(Config.CONSUMER_KEY, Config.CONSUMER_SECRET)
        auth.set_access_token(Config.ACCESS_TOKEN, Config.ACCESS_TOKEN_SECRET)
        self.api = API(auth)

    def start(self):
        me = self.api.me()
        print(f"AutoFess started on @{me.screen_name}. Hi.")

    def get_api(self):
        return self.api
