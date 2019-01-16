from pymongo import MongoClient
from loguru import logger
from model import ICMMRunner

class RunnerDB():
    MONGO_CLIENT = None
    DB = None
    COLLECTION = None

    @classmethod
    def init(cls, mongodb_uri, database_name):
        cls.MONGO_CLIENT = MongoClient(mongodb_uri)
        cls.DB = cls.MONGO_CLIENT[database_name]
        logger.info('Initialized database connection')

    @classmethod
    def set_collection(cls, collection_name):
        cls.COLLECTION = cls.DB[collection_name]
        logger.info('Set {} as collection'.format(collection_name))

    @classmethod
    def close(cls):
        cls.MONGO_CLIENT.close()
        logger.info('Closed database collection')

    ##################
    # ICMMRunner
    ##################
    @classmethod
    def find_one_runner(cls, query={}):
        sub_doc = cls.COLLECTION.find_one(query)
        if sub_doc:
            return ICMMRunner.from_doc(sub_doc)
        else:
            return None

    @classmethod
    def find_runner(cls, query={}):
        sub_cursor = cls.COLLECTION.find(query)
        return [ICMMRunner.from_doc(sub_doc) for sub_doc in sub_cursor]

    @classmethod
    def insert_runner(cls, runner):
        assert type(runner) == ICMMRunner
        logger.info('Insert runner: {}', runner)
        # Get result _id by inserted_id attribute
        return cls.COLLECTION.insert_one(runner.to_doc())

    @classmethod
    def insert_runners(cls, runners):
        sub_docs = []
        for runner in runners:
            assert type(runner) == ICMMRunner
            sub_docs.append(runner.to_doc())
            logger.info('Insert runner: {}', str(runner))
        # Get result _id by inserted_id attribute
        return cls.COLLECTION.insert_many(sub_docs)

    @classmethod
    def update_one_runner(cls, query, runner, upsert=False):
        logger.info('Update runner: {}', str(runner))
        return cls.COLLECTION.update_one(query, {'$set': runner.to_doc()}, upsert=upsert)

    @classmethod
    def update_one_runner_feedback(cls, query, feedback, challenge_result, upsert=False):
        logger.info('Update runner\'s feedback: {}', str(feedback))
        set_query = {'$set': {'feedback': feedback, 'challengeResult': challenge_result}}
        return cls.COLLECTION.update_one(query, set_query, upsert=upsert)
