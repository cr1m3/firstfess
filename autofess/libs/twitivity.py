import json
import hmac
import hashlib
import base64
import re
import requests

from abc import ABC, abstractmethod
from .. import config
from tweepy import OAuthHandler
from flask import Flask, request
from threading import Thread


class Activity:
    _protocol: str = "https:/"
    _host: str = "api.twitter.com"
    _version: str = "1.1"
    _product: str = "account_activity"
    _env_name: str = config.ENV_NAME
    _auth: OAuthHandler = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    _auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    def api(self, method: str, endpoint: str, data: dict = None) -> json:
        """
        :param method: GET or POST
        :param endpoint: API Endpoint to be specified by user
        :param data: POST Request payload parameter
        :return: json
        """
        with requests.Session() as r:
            response = r.request(
                url="/".join(
                    [
                        self._protocol,
                        self._host,
                        self._version,
                        self._product,
                        endpoint,
                    ]
                ),
                method=method,
                auth=self._auth.apply_auth(),
                data=data,
            )
            return response

    def register_webhook(self, callback_url: str) -> json:
        return self.api(
            method="POST",
            endpoint=f"all/{self._env_name}/webhooks.json",
            data={"url": callback_url},
        )

    def delete_webhook(self, webhook_id: int) -> json:
        return self.api(
            method="DELETE",
            endpoint=f"all/{self._env_name}/webhooks/{webhook_id}.json",
        )

    def subscribe(self) -> json:
        return self.api(
            method="POST", endpoint=f"all/{self._env_name}/subscriptions.json",
        )


def url_params(url: str) -> str:
    pattern: str = r"^[^\/]+:\/\/[^\/]*?\.?([^\/.]+)\.[^\/.]+(?::\d+)?\/"
    return re.split(pattern=pattern, string=url)[-1]


class Event(ABC):
    CALLBACK_URL: str = config.CALLBACK_URL

    def __init__(self):
        self._server = self._get_server()

    @abstractmethod
    def on_data(self, data: json) -> None:
        pass

    def listen(self) -> None:
        thread = Thread(target=self._server.run)
        thread.start()

    def _get_server(self) -> Flask:
        try:
            app = Flask(__name__)
            app.debug = False

            @app.route(f"/{url_params(url=self.CALLBACK_URL)}", methods=["GET", "POST"])
            def callback() -> json:
                if request.method == "GET":
                    hash_digest = hmac.digest(
                        key=config.CONSUMER_SECRET.encode("utf-8"),
                        msg=request.args.get("crc_token").encode("utf-8"),
                        digest=hashlib.sha256,
                    )
                    return {
                        "response_token": "sha256="
                        + base64.b64encode(hash_digest).decode("ascii")
                    }
                elif request.method == "POST":
                    data = request.get_json()
                    self.on_data(data)
                    return {"code": 200}

            return app
        except Exception:
            raise
