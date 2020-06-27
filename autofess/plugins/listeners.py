from tweepy import Cursor, TweepError
from ..fess import AutoFess
from ..config import Config
from ..utils import database
import time

TRIGGER_WORD = Config.TRIGGER_WORD.split("-")
BLACKLIST_WORD = Config.BLACKLIST_WORD.split("-")

api = AutoFess().get_api()
chunk_size = 240

def split_chunk(text, chunk_size):
	return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def filter_check(text):
    if (any(i in text.split() for i in BLACKLIST_WORD) and 
            any(j in text for j in TRIGGER_WORD)):
        return False
    return True

def get_new_dms():
    dms = api.list_direct_messages() # Get last 15 direct messages
    new_dms = []
    for dm in dms:
        dm_id = dm.id
        dm_sender_id = dm.message_create['sender_id']
        dm_text = dm.message_create['message_data']['text']

        # Fetch if already posted or doesnt contain trigger word
        if database.get(dm_id) or not filter_check(dm_text):
            continue

        database.put(dm_id, dm_sender_id)
        new_dms.append(dm_text)
    return new_dms

def send_status(text, reply_to_id = 0):
	update_ret = api.update_status(text,
					in_reply_to_status_id=reply_to_id)
	return update_ret.id

while True:
    new_dms = get_new_dms()
    for new_dm in new_dms:
        reply_id = 0
        try:
            chunked = split_chunk(new_dm, chunk_size)
            for chunk in chunked:
                reply_id = send_status(chunk, reply_id)
                time.sleep(15)
        except TweepError as e:
            print(e)
            pass
    time.sleep(60)
