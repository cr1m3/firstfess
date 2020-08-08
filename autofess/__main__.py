import atexit
import time
from threading import Thread

from autofess import fess, plugins

stream_event = plugins.streamer.StreamEvent()
autofess = fess.AutoFess()

if __name__ == "__main__":
    autofess.start()
    stream_event.listen()
    time.sleep(3)  # Sleep to wait until webhook is initialized
    webhook_id = autofess.configure_webhook()
    atexit.register(autofess.delete_webhook, webhook_id=webhook_id)
