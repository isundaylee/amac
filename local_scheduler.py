import scheduler
import ujson

from logger import Logger

class LocalScheduler(scheduler.Scheduler):
    results = []

    def __init__(self, initialURLs, outputFile):
        self.urlQueue = initialURLs
        self.logger = Logger('SCHEDULER')
        self.outputFile = outputFile

    def popURL(self):
        if len(self.urlQueue) == 0:
            return None
        else:
            return self.urlQueue.pop()

    def pushURL(self, category, url):
        self.urlQueue.append((category, url))
        self.logger.log("Pushing URL: " + category + " ==> " + url)

    def commitResults(self, results):
        self.logger.log("Committing %d results" % len(results))
        self.results.extend(results)
        with open(self.outputFile, 'w') as file:
            file.write(ujson.dumps(self.results))
