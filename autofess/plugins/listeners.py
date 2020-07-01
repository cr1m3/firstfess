from tweepy import TweepError
from autofess import utils, config, fess
from requests_oauthlib import OAuth1
import requests
import os
import time
import spintax

TRIGGER_WORD = config.TRIGGER_WORD.split("-")
BLACKLIST_WORD = config.BLACKLIST_WORD.split("-")


def split_chunk(text):
    chunk_size = 240
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def is_triggered(text):
    return any(i in text.split() for i in BLACKLIST_WORD) is False and any(
        j in text for j in TRIGGER_WORD
    )


def dl_media(media_url):
    auth = OAuth1(
        client_key=config.CONSUMER_KEY,
        client_secret=config.CONSUMER_SECRET,
        resource_owner_key=config.ACCESS_TOKEN,
        resource_owner_secret=config.ACCESS_TOKEN_SECRET,
    )
    r = requests.get(media_url, auth=auth)
    file_name = "image/" + media_url.split("/")[-1]
    with open(file_name, "wb") as f:
        f.write(r.content)
    return file_name


def is_media(message_data):
    if "attachment" not in message_data:
        return False
    return True


class Listeners:
    db = utils.database.Datafess("listen_fess")

    def __init__(self):
        self.api = fess.AutoFess().get_api()
        self.me = self.api.me()

    def get_new_dms(self):
        dms = self.api.list_direct_messages()  # Get last 15 direct messages
        new_dms = []
        for dm in dms:
            dm_id = dm.id
            dm_sender_id = dm.message_create["sender_id"]
            dm_data = dm.message_create["message_data"]

            if self.db.get(dm_id) or int(dm_sender_id) == self.me.id:
                continue

            self.db.put(dm_id, dm_sender_id)
            dm_data["sender_id"] = dm_sender_id
            new_dms.append(dm_data)
        return new_dms

    def send_status_with_media(self, text, media_url):
        media_file = dl_media(media_url)
        update_ret = self.api.update_with_media(media_file, status=text)
        os.remove(media_file)
        return update_ret.id

    def send_status(self, text, reply_to_id=0):
        update_ret = self.api.update_status(text, in_reply_to_status_id=reply_to_id)
        return update_ret.id

    def process_fess(self, direct_message):
        reply_id = 0
        dm_text = direct_message["text"]
        if not is_triggered(dm_text):
            return config.FILTERED_MESSAGE

        chunked = split_chunk(dm_text)
        username = self.me.screen_name
        try:
            if is_media(direct_message):
                attachment = direct_message["attachment"]
                media_url = attachment["media"]["media_url_https"]
                chunked[-1] = chunked[-1].rsplit(" ", 1)[0]  # Remove t.co/....
                reply_id = self.send_status_with_media(chunked[0], media_url)
            else:
                reply_id = self.send_status(chunked[0], reply_id)

            fess_url = f" https://twitter.com/{username}/status/{reply_id}"
            reply_text = config.SUCCESS_MESSAGE + fess_url
            del chunked[0]

            for chunk in chunked:
                time.sleep(10)
                reply_id = self.send_status(chunk, reply_id)
        except TweepError as e:
            reply_text = config.ERROR_MESSAGE
            print(e)
        return reply_text

    def main(self):
        while True:
            new_dms = self.get_new_dms()
            for new_dm in new_dms:
                recipient_id = new_dm["sender_id"]
                reply_text = self.process_fess(new_dm)
                self.api.send_direct_message(recipient_id, spintax.spin(reply_text))
                time.sleep(15)
            time.sleep(60)
