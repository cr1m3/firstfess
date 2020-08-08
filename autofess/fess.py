from autofess import config
from tweepy import API, OAuthHandler

from .libs import twitivity


class AutoFess:
    def __init__(self):
        auth = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
        auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
        self.api = API(auth, retry_count=10, retry_delay=5, retry_errors={503})

    def start(self):
        me = self.api.me()
        print(f"AutoFess started on @{me.screen_name}. Hi.")

    def get_api(self):
        return self.api

    @staticmethod
    def configure_webhook():
        activity = twitivity.Activity()
        resp = activity.register_webhook(callback_url=config.CALLBACK_URL)
        activity.subscribe()
        return resp.json()["id"]

    @staticmethod
    def delete_webhook(webhook_id):
        activity = twitivity.Activity()
        resp = activity.delete_webhook(webhook_id=webhook_id)
