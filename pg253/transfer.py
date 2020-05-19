from subprocess import Popen, PIPE
import datetime

from pg253.clientS3 import ClientS3


class Transfer:
    def __init__(self, config, database, metrics):
        self.database = database
        self.metrics = metrics
        self.buffer_size = int(config.buffer_size)
        self.buffer = bytearray(self.buffer_size)
        now = datetime.datetime.now()
        self.key = ('postgres.%s.%s.dump'
                    % (database, now.strftime('%Y%m%d-%H%M')))
        print(self.key)
        self.client = ClientS3(config)

    def run(self):
        input_cmd = 'pg_dump -Fc -v -d %s' % self.database
        upload = self.client.createMultipartUpload(self.key)
        self.metrics.resetTransfer(self.database)

        print('%s --> %s' % (input_cmd, self.key))
        with Popen(input_cmd.split(), stdout=PIPE, stderr=PIPE) as input:
            while True:

                self.metrics.setPart(self.database, upload.getPart())

                # Retrieve data from input in the buffer
                bytes_read = input.stdout.readinto(self.buffer)
                self.metrics.incrementRead(self.database, bytes_read)

                if bytes_read == 0:
                    break

                # Push buffer to object storage
                res = upload.uploadPart(self.buffer,
                                        bytes_read,
                                        self.buffer_size)
                print(res)
                self.metrics.incrementWrite(self.database, bytes_read)
                print('Write %s bytes' % bytes_read)

            if input.poll() is not None:
                if self.metrics.getCurrentRead(self.database) == 0 or input.returncode != 0:
                    upload.abort()
                    raise Exception('Error: no data transfered or error on pg_dump: %s'
                                    % input.stderr.read())
                else:
                    upload.complete()
                print('%s bytes written' % self.metrics.getCurrentWrite(self.database))
            else:
                raise Exception('Read of input finished but process is not finished, should not happen')

        print('Done')
