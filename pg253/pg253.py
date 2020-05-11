from pg253.metrics import Metrics
from pg253.cluster import Cluster
from pg253.configuration import Configuration


def main():
    config = Configuration()
    print(config)
    metrics = Metrics()
    cluster = Cluster(metrics)
    print(cluster.listDatabase())
    cluster.backup()


if __name__ == '__main__':
    main()
