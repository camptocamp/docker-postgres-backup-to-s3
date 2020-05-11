from pg253.transfer import Transfer

class Cluster:
    def __init__(self, metrics):
        self.metrics = metrics

    def listDatabase(self):
        return ['postgres']

    def backup(self):
        for database in self.listDatabase():
            print("Begin backup of '%s' database" % database)
            transfer = Transfer(database, self.metrics)
            transfer.run()
            print('End backup of %s' % database)
