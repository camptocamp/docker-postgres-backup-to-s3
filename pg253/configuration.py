import os


class Configuration:

    # Source configuration
    # --------------------
    PGHOST = 'PGHOST'
    PGUSER = 'PGUSER'
    PGPASSWORD = 'PGPASSWORD'
    # Regexp for DB exclusion (DBs that match this regexp will not be backuped)
    BLACKLISTED_DATABASES = 'BLACKLISTED_DATABASES'

    # Buffer configuration
    # --------------------
    BUFFER_SIZE = 'BUFFER_SIZE'

    # Target configuration
    # --------------------
    # Size of upload part and internal buffer
    AWS_ENDPOINT = 'AWS_ENDPOINT'
    AWS_S3_BUCKET = 'AWS_S3_BUCKET'
    AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
    AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'

    # Exporter configuration
    # ----------------------
    PROMETHEUS_EXPORTER_PORT = 'PROMETHEUS_EXPORTER_PORT'

    def __init__(self):
        # Default value
        self._setupDefault(Configuration.PROMETHEUS_EXPORTER_PORT, 9352)
        self._setupDefault(Configuration.BUFFER_SIZE, 10 * 1024 * 1024)  # 10MB

        # Test configuration:
        # Source configuration
        self._setupDefault(Configuration.PGHOST, 'postgres')
        self._setupDefault(Configuration.PGUSER, 'postgres')
        self._setupDefault(Configuration.PGPASSWORD, 'pgpass')
        self._setupDefault(Configuration.BLACKLISTED_DATABASES,
                           ".*backup.*|postgres|rdsadmin")

        # Target configuration
        self._setupDefault(Configuration.AWS_ENDPOINT, 'http://localhost:9000')
        self._setupDefault(Configuration.AWS_S3_BUCKET, 'postgres-to-s3')
        self._setupDefault(Configuration.AWS_ACCESS_KEY_ID, 'AKIAACCESSKEY')
        self._setupDefault(Configuration.AWS_SECRET_ACCESS_KEY, 'SECRETSECRET')


    def _setupDefault(self, key, value):
        os.environ[key] = os.getenv(key, str(value))

    def __str__(self):
        res = ''
        res += "Source configuration:\n"
        res += "\tHost : %s\n" % os.environ[Configuration.PGHOST]
        res += "\tUser : %s\n" % os.environ[Configuration.PGUSER]
        res += ("\tPassword : %s\n"
                % ('X' * len(os.environ[Configuration.PGPASSWORD])))
        res += ("\tBlacklisted DBs: %s\n"
                % os.environ[Configuration.BLACKLISTED_DATABASES])
        res += "Buffer configuration:\n"
        res += ("\tBuffer size: %s\n"
                % sizeof_fmt(os.environ[Configuration.BUFFER_SIZE]))
        res += "Target configuration:\n"
        res += ("\tEndpoint: %s\n"
                % os.environ[Configuration.AWS_ENDPOINT])
        res += ("\tBucket: %s\n"
                % os.environ[Configuration.AWS_S3_BUCKET])
        res += ("\tAccess Key: %s\n"
                % os.environ[Configuration.AWS_ACCESS_KEY_ID])
        res += ("\tSecret Key : %s\n"
                % ('X' * len(os.environ[Configuration.AWS_SECRET_ACCESS_KEY])))
        return res


def sizeof_fmt(num):
    num = int(num)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(num) < 1024.0:
            return "%3.1f%s" % (num, unit)
        else:
            num /= 1024.0
    return "%.1f%s" % (num, 'TB')
