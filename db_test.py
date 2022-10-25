import pymongo
import uuid

import os
import certifi

CA = certifi.where()

DB_PASSWORD = os.getenv("DB_PASSWORD")
MAC_ADDRESS = str(hex(uuid.getnode()))
NUM_TOKENS = 42

if __name__ == '__main__':
    client = pymongo.MongoClient(f"mongodb+srv://DanielSkala:{DB_PASSWORD}@digistudydemo.ih5ikoh"
                                 f".mongodb.net/?retryWrites=true&w=majority", tlsCAFile=CA)
    db = client["users"]
    col = db["usage"]

    # col.insert_one({"_id": MAC_ADDRESS, "num_tokens": 0})

    # col.update_one({"_id": MAC_ADDRESS}, {"$set": {"num_tokens": NUM_TOKENS}})

    address = col.find_one({"_id": MAC_ADDRESS+"sd"})
    print(address)