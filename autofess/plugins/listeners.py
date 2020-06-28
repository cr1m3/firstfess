from tweepy import Cursor, TweepError
from ..fess import AutoFess
from ..config import Config
from ..utils import database
from requests_oauthlib import OAuth1
import requests
import os
import time

TRIGGER_WORD = Config.TRIGGER_WORD.split("-")
BLACKLIST_WORD = Config.BLACKLIST_WORD.split("-")

api = AutoFess().get_api()
chunk_size = 240

def split_chunk(text, chunk_size):
	return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def is_triggered(text):
	return (any(i in text.split() for i in BLACKLIST_WORD) is False and
			any(j in text for j in TRIGGER_WORD))

def get_new_dms():
	dms = api.list_direct_messages() # Get last 15 direct messages
	new_dms = []
	for dm in dms:
		dm_id = dm.id
		dm_sender_id = dm.message_create['sender_id']
		dm_data = dm.message_create['message_data']

		if database.get(dm_id):
			continue

		database.put(dm_id, dm_sender_id)
		new_dms.append(dm_data)
	return new_dms

def dl_media(media_url):
	auth = OAuth1(client_key = Config.CONSUMER_KEY,
				client_secret = Config.CONSUMER_SECRET,
				resource_owner_key = Config.ACCESS_TOKEN,
				resource_owner_secret = Config.ACCESS_TOKEN_SECRET)
	r = requests.get(media_url, auth = auth)
	file_name = "image/" + media_url.split("/")[-1]
	with open(file_name, 'wb') as f:
		f.write(r.content)
	return file_name

def is_media(message_data):
	if not "attachment" in message_data:
		return False
	elif message_data["attachment"]["type"] == "media":
		return True

def send_status_with_media(text, media_url):
	media_file = dl_media(media_url)
	update_ret = api.update_with_media(media_file, status=text)
	os.remove(media_file)
	return update_ret.id

def send_status(text, reply_to_id = 0):
	update_ret = api.update_status(text,
					in_reply_to_status_id=reply_to_id)
	time.sleep(1)
	return update_ret.id

while True:
	new_dms = get_new_dms()
	for new_dm in new_dms:
		reply_id = 0
		dm_text = new_dm["text"]
		if not is_triggered(dm_text):
			continue
		try:
			chunked = split_chunk(dm_text, chunk_size)
			if is_media(new_dm):
				media_url = new_dm["attachment"]["media"]["media_url_https"]
				chunked[-1] = chunked[-1].rsplit(' ', 1)[0] # Remove t.co/....
				reply_id = send_status_with_media(chunked[0], media_url)
				del chunked[0]

			for chunk in chunked:
				reply_id = send_status(chunk, reply_id)
			time.sleep(15)
		except TweepError as e:
			print(e)
			pass
	time.sleep(60)
