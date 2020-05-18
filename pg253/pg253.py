import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from pg253.metrics import Metrics
from pg253.cluster import Cluster
from pg253.configuration import Configuration


def main():
    config = Configuration()
    print(config)
    metrics = Metrics()
    cluster = Cluster(metrics)
    print(cluster.listDatabase())

    # Start scheduler
    scheduler = BlockingScheduler()
    scheduler.add_executor('processpool')
    scheduler.add_job(cluster.backup,
                      CronTrigger.from_crontab(os.environ[Configuration.SCHEDULE]))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass



if __name__ == '__main__':
    main()
