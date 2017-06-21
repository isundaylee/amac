class Logger:
    def __init__(self, tag):
        self.tag = tag

    def log(self, message):
        print("     [%10s] %s" % (self.tag, message))

    def exception(self, message):
        print("!!!! [%10s] %s" % (self.tag, message))
