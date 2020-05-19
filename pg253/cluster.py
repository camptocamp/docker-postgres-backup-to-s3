import re
from datetime import datetime
from subprocess import run

from pg253.transfer import Transfer


class Cluster:
    def __init__(self, config, metrics):
        self.config = config
        self.metrics = metrics
        self.db_exclude = re.compile(config.blacklisted_databases)
        print("OK")

    def listDatabase(self):
        cmd = ['psql', '-qAtX', '-c', '"SELECT datname FROM pg_database"']
        res = run(cmd, capture_output=True)
        if res.returncode != 0:
            raise Exception('Unable to retrieve database list: %s' % res.stderr.decode())
        dbs = res.stdout.decode().strip().split("\n")
        dbs = list(filter(lambda x: not self.db_exclude.search(x), dbs))
        dbs.remove('template0')
        return dbs

    def backup(self):
        for database in self.listDatabase():
            backup_start = datetime.now()
            print("Begin backup of '%s' database" % database)
            transfer = Transfer(self.config, database, self.metrics)
            transfer.run()
            backup_end = datetime.now()
            self.metrics.setLastBackup(database, backup_end)
            self.metrics.setBackupDuration(database, backup_end.timestamp() - backup_start.timestamp())
            print('End backup of %s' % database)
