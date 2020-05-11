import re
import os
from subprocess import run

from pg253.transfer import Transfer
from pg253.configuration import Configuration

class Cluster:
    def __init__(self, metrics):
        self.metrics = metrics
        self.db_exclude = re.compile(os.environ[Configuration.BLACKLISTED_DATABASES])
        print("OK")

    def listDatabase(self):
        cmd = ['psql', '-qAtX', '-c', '"SELECT datname FROM pg_database"']
        res = run(cmd, capture_output=True)
        dbs = res.stdout.decode().strip().split("\n")
        dbs = list(filter(lambda x: not self.db_exclude.search(x), dbs))
        dbs.remove('template0')
        return dbs

    def backup(self):
        for database in self.listDatabase():
            print("Begin backup of '%s' database" % database)
            transfer = Transfer(database, self.metrics)
            transfer.run()
            print('End backup of %s' % database)
