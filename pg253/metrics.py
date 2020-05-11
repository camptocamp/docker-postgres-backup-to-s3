import os

from prometheus_client import start_http_server
from prometheus_client import Gauge, Counter

from pg253.configuration import Configuration


class Metrics:
    def __init__(self):
        self.current_read = 0
        self.current_write = 0

        # Start and configure prometheus exporter
        start_http_server(int(os.environ[Configuration.PROMETHEUS_EXPORTER_PORT]))

        self.total_bytes_read = (
            Counter('total_bytes_read',
                    'Total bytes reads from input'))
        self.current_bytes_read = (
            Gauge('current_bytes_read',
                  'Bytes reads from input for current transfer'))
        self.total_bytes_write = (
            Counter('total_bytes_write',
                    'Total bytes uploaded to object storage'))
        self.current_bytes_write = (
            Gauge('current_bytes_write',
                  'Bytes uploaded to object storage for current transfer'))
        self.part_count = (
            Gauge('part_count',
                  'Part of the Multipart upload uploaded'))

    def resetTransfer(self):
        self.current_bytes_read.set(0)
        self.current_bytes_write.set(0)
        self.current_read = 0
        self.current_write = 0

    def incrementRead(self, count):
        self.current_bytes_read.inc(count)
        self.current_read += count
        self.total_bytes_read.inc(count)

    def incrementWrite(self, count):
        self.current_bytes_write.inc(count)
        self.current_write += count
        self.total_bytes_write.inc(count)

    def setPart(self, count):
        self.part_count.set(count)

    def getCurrentRead(self):
        return self.current_read

    def getCurrentWrite(self):
        return self.current_write
