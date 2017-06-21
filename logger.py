class Logger:
    def __init__(self, tag):
        self.tag = tag

    def log(self, message):
        print("     [%10s] %s" % (self.tag, message))

    def exception(self, ex):
        print("!!!! [%10s] Exception: %s" % (self.tag, str(ex)))
