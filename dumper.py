import redis
import ujson

class Dumper:
    def __init__(self, host, port, db):
        self.redis = redis.StrictRedis(host=host, port=port, db=db)

    def dump(self):
        count = self.redis.llen('results')
        results = []
        for i in range(count):
            result = ujson.loads(self.redis.lindex('results', i))
            results.append(result)
        return ujson.dumps(results)

if __name__ == '__main__':
    print(Dumper('localhost', 6379, 0).dump())
