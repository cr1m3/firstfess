from tweepy import Cursor, TweepError
from ..fess import AutoFess
from ..config import Config
from ..utils import database
import time

api = AutoFess().get_api()
chunk_size = 240

def split_chunk(text, chunk_size):
	return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_new_dms():
    dm = api.list_direct_messages() # Get last 15 direct messages
    new_dms = []
    for i in dm:
        dm_id = i.id
        dm_sender_id = i.message_create['sender_id']
        dm_text = i.message_create['message_data']['text']

        # Fetch if already posted or doesnt contain trigger word
        if database.get(dm_id) or Config.TRIGGER_WORD not in dm_text:
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
