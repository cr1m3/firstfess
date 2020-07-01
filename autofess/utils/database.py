import plyvel
import msgpack


def _encode(value):
    return msgpack.packb(value, use_bin_type=True)


def _decode(value):
    return msgpack.unpackb(value, raw=False)


class Datafess:
    def __init__(self, db):
        self._db = plyvel.DB("database/" + db, create_if_missing=True)

    def put(self, key, value):
        value = _encode(value)
        return self._db.put(key.encode("utf-8"), value)

    def get(self, key):
        return self._db.get(key.encode("utf-8"))

    def delete(self, key):
        return self._db.delete(key.encode("utf-8"))
