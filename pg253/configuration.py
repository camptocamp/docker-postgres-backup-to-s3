import os

class Configuration:

    CONFIG = {'SCHEDULE': '20 2 * * *',
              'PROMETHEUS_EXPORTER_PORT': '9352',
              'BUFFER_SIZE': str(10 * 1024 * 1024),
              'PGHOST': None,
              'PGUSER': None,
              'PGPASSWORD': None,
              'BLACKLISTED_DATABASES': '.*backup.*|postgres|rdsadmin',
              'AWS_ENDPOINT': None,
              'AWS_S3_BUCKET': None,
              'AWS_ACCESS_KEY_ID': None,
              'AWS_SECRET_ACCESS_KEY': None,
              }

    def __getattribute__(self, obj):
        if obj.upper() not in Configuration.CONFIG:
            raise Exception('Unknown config key: %s' % obj)
        # return value from env
        if obj.upper() in os.environ:
            return os.environ[obj.upper()]
        # return default value
        if Configuration.CONFIG[obj.upper()] is not None:
            return Configuration.CONFIG[obj.upper()]
        else:
            raise Exception('Missing value for %s' % obj)

    def __set__(self, obj, value):
        setattr(obj, self.attr, value + ' unicorns')

    def __str__(self):
        res = ''
        res += "Source configuration:\n"
        res += "\tHost : %s\n" % self.pghost
        res += "\tUser : %s\n" % self.pguser
        res += "\tPassword : %s\n" % ('X' * len(self.pgpassword))
        res += "\tBlacklisted DBs: %s\n" % self.blacklisted_databases
        res += "Buffer configuration:\n"
        res += "\tBuffer size: %s\n" % sizeof_fmt(self.buffer_size)
        res += "Target configuration:\n"
        res += "\tEndpoint: %s\n" % self.aws_endpoint
        res += "\tBucket: %s\n" % self.aws_s3_bucket
        res += "\tAccess Key: %s\n" % self.aws_access_key_id
        res += "\tSecret Key : %s\n" % ('X' * len(self.aws_secret_access_key))
        return res


def sizeof_fmt(num):
    num = int(num)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(num) < 1024.0:
            return "%3.1f%s" % (num, unit)
        else:
            num /= 1024.0
    return "%.1f%s" % (num, 'TB')
