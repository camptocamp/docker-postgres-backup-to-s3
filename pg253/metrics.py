import re
import datetime

from prometheus_client import start_http_server
from prometheus_client import Gauge, Counter

from pg253.clientS3 import ClientS3


class Metrics:
    def __init__(self, config):
        self.config = config
        self.current_read = {}
        self.current_write = {}

        # Start and configure prometheus exporter
        start_http_server(int(config.prometheus_exporter_port))

        self.total_bytes_read = (
            Counter('total_bytes_read',
                    'Total bytes reads from input'))
        self.current_bytes_read = (
            Gauge('current_bytes_read',
                  'Bytes reads from input for current transfer',
                  ['database']))
        self.total_bytes_write = (
            Counter('total_bytes_write',
                    'Total bytes uploaded to object storage'))
        self.current_bytes_write = (
            Gauge('current_bytes_write',
                  'Bytes uploaded to object storage for current transfer',
                  ['database']))
        self.part_count = (
            Gauge('part_count',
                  'Part of the Multipart upload uploaded',
                  ['database']))
        self.first_backup = (
            Gauge('first_backup',
                  'Date of first backup',
                  ['database']))
        self.last_backup = (
            Gauge('last_backup',
                  'Date of last backup',
                  ['database']))
        self.backups = (
            Gauge('backups',
                  'All backups',
                  ['database', 'date']))
        self.backup_duration = (
            Gauge('backup_duration',
                  'Duration of backup',
                  ['database']))
        self.readRemoteBackup()


    def readRemoteBackup(self):

        parse_filename = re.compile(r'postgres.([^\.]+).([^\.]+).dump')
        client = ClientS3(self.config)

        first_backups = {}
        last_backups = {}

        for item in client.listContent('/'):
            print(item)
            if parse_filename.search(item):
                matches = parse_filename.match(item)
                database = matches.group(1)
                date = datetime.datetime.strptime(matches.group(2), '%Y%m%d-%H%M')
                if database not in first_backups or date.timestamp() < first_backups[database]:
                    first_backups[database] = date.timestamp()
                if database not in last_backups or date.timestamp() > last_backups[database]:
                    last_backups[database] = date.timestamp()
                self.backups.labels(database, matches.group(2)).set(date.timestamp())
        for database in first_backups:
            self.first_backup.labels(database).set(first_backups[database])
        for database in last_backups:
            self.last_backup.labels(database).set(last_backups[database])

    def setLastBackup(self, database, backup_datetime):
        self.last_backup.labels(database).set(backup_datetime.timestamp())

    def setBackupDuration(self, database, duration):
        self.backup_duration.labels(database).set(duration)

    def resetTransfer(self, database):
        self.current_bytes_read.labels(database).set(0)
        self.current_bytes_write.labels(database).set(0)
        self.current_read[database] = 0
        self.current_write[database] = 0

    def incrementRead(self, database, count):
        self.current_bytes_read.labels(database).inc(count)
        self.current_read[database] += count
        self.total_bytes_read.inc(count)

    def incrementWrite(self, database, count):
        self.current_bytes_write.labels(database).inc(count)
        self.current_write[database] += count
        self.total_bytes_write.inc(count)

    def setPart(self, database, count):
        self.part_count.labels(database).set(count)

    def getCurrentRead(self, database):
        return self.current_read[database]

    def getCurrentWrite(self, database):
        return self.current_write[database]
