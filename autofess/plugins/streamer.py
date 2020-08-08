import json
import spintax

from ..libs import twitivity
from autofess import config
from .responder import Responders

responders = Responders()
me = responders.me


class StreamEvent(twitivity.Event):
    def on_data(self, data: json) -> None:
        if "direct_message_events" in data:
            message = data["direct_message_events"][0]["message_create"]
            sender_id = message["sender_id"]
            if int(sender_id) == me.id:
                return
            text = message["message_data"]["text"]
            reply_text = responders.process_fess(message)
            responders.api.send_direct_message(sender_id, spintax.spin(reply_text))
