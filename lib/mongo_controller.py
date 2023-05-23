import traceback
import motor.motor_asyncio

from pymongo.errors import DuplicateKeyError
from lib.settings import Settings

class MongoController(object):
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(Settings.mongo_uri)
        self.db = self.client[Settings.mongo_db]
        self.pmrs = self.db['pmrs']

    async def count(self):
        doc_num = await self.pmrs.count_documents({})
        return doc_num

    def find(self, args):
        return self.pmrs.find(args)

    async def find_one(self, args):
        doc = await self.pmrs.find_one(args)
        return doc

    async def delete_one(self, args):
        res = await self.pmrs.delete_one(args)
        return res.deleted_count > 0

    def sanitize(self, mystr):
        return mystr.replace("~", "~e").replace(".", "~p").replace("$", "~d")

    def desanitize(self, mystr):
        return mystr.replace("~d", "$").replace("~p", ".").replace("~e", "~")

    async def update(self, doc):
        try:
            result = await self.pmrs.update_one({'address': doc['address'], 'personId':doc['personId']}, {'$set': doc}, upsert=True)
            print('updated {0} document, upserted_id: {1}'.format(result.modified_count, result.upserted_id))
        except DuplicateKeyError as de:
            result = "DuplicateKeyError"
        return result


