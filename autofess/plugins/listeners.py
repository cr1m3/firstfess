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

        # Message cant exceed 500 characters (to prevent spam)
        if len(dm_text) > 500:
            continue

        database.put(dm_id, dm_sender_id)
        new_dms.append(dm_text)
    return new_dms

def send_status(text, reply_to_id = 0):
    len_text = len(text)
    if len_text < 240 and reply_to_id == 0:
        return api.update_status(text)
    elif len_text > 240 and reply_to_id == 0:
        status = text[:240]
        update_ret = api.update_status(status + "(cont.)")
        rest_status = 500 - len(status) - 47 # TODO Remove 47
        return send_status(text[-rest_status:], update_ret.id)
    else:
        return api.update_status(text, in_reply_to_status_id=reply_to_id)

while True:
    new_dms = get_new_dms()
    for i in new_dms:
        send_status(i)
        time.sleep(10)
    time.sleep(30)
