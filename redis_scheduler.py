import scheduler
import ujson
import redis

from logger import Logger

class RedisScheduler(scheduler.Scheduler):
    def __init__(self, initialURLs, host, port, db):
        self.logger = Logger('SCHEDULER')
        self.redis = redis.StrictRedis(host=host, port=port, db=db)

        if self.redis.getset('initialized', 1) is None:
            self.logger.log("Starting afresh")
            for url in initialURLs:
                self.pushURL(url[0], url[1])
        else:
            self.logger.log("Resuming")

    def popURL(self):
        raw_url = self.redis.lpop('urls')
        if raw_url is None:
            return None

        url = ujson.loads(raw_url)
        return (url['category'], url['url'])


    def pushURL(self, category, url):
        self.redis.lpush('urls', ujson.dumps({
            'category': category,
            'url': url,
        }))

        self.logger.log("Pushing URL: " + category + " ==> " + url)

    def commitResults(self, results):
        self.logger.log("Committing %d results" % len(results))

        for result in results:
            self.redis.lpush('results', ujson.dumps(result))
