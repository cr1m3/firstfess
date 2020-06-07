from tweepy import Cursor
from ..fess import AutoFess
from ..config import Config
from ..utils import database
import time

api = AutoFess().get_api()

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

while True:
    new_dms = get_new_dms()
    for i in new_dms:
        api.update_status(i)
        time.sleep(10)
    time.sleep(5)
