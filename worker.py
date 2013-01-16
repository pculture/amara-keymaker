from redis import Redis
from rq import Worker, Queue, Connection
import config

listen = ['high', 'default', 'low']
conn = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
        db=config.REDIS_DB, password=config.REDIS_PASSWORD)

with Connection(conn):
    worker = Worker(map(Queue, listen))
    worker.work()
