import plyvel

# Plyvel
postDB = plyvel.DB("database/post.db", create_if_missing=True)


def intToBytes(key):
    return bytes(str(key), "utf-8")


def put(key, value):
    return postDB.put(bytes(key, "utf-8"), bytes(value, "utf-8"))


def get(key):
    return postDB.get(bytes(key, "utf-8"))


def delete(key):
    return postDB.delete(bytes(key, "utf-8"))
