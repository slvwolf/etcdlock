# coding=utf-8
import argparse
import subprocess
import etcd
import uuid

"""
Distributed lock/mutex using etcd (https://github.com/coreos/etcd)

Usage:

    lock = EtcdLock("/locks/my_lock", "service_1")
    lock.acquire()
    ...
    lock.release()

    # Or

    with EtcdLock("/locks/my_lock", "service_1"):
        ...
"""
class EtcdLock:

    def __init__(self, key, id, host='127.0.0.1', port=4001, protocol='http'):
        self._id = id
        self._key = key
        self._client = etcd.Client(host=host, port=port, protocol=protocol)

    """ Block until lock is acquired """
    def acquire(self):
        while not self._try_acquire():
           self._client.read(self._key, wait=True)

    def _try_acquire(self):
        try:
            result = self._client.read(self._key)
        except etcd.EtcdKeyNotFound:
            try:
                result = self._client.write(self._key, self._id, prevExist=False)
            except etcd.EtcdAlreadyExist:
                # Too late, someone else got the lock already
                return False
        return result.value == self._id

    """ Release lock """
    def release(self):
        self._client.delete(self._key, prevValue=self._id)

    def __enter__(self):
        self.acquire()

    def __exit__(self, type, value, tb):
        self.release()


class EtcdLockCmd:

    def __init__(self):
        self._args = {}

    def run(self):
        with EtcdLock(self._args.key, self._args.id):
            subprocess.call(" ".join(self._args.cmd), shell=True)

    def main(self):
        parser = argparse.ArgumentParser(description='Command line lock using Etcd')
        parser.add_argument(
            '--key', help='Key used for lock (Default: /lock/default)', default='/lock/default')
        parser.add_argument(
            '--id', help='Client id for the lock. This should be unique for each client (Default: generated)', default=str(uuid.uuid4()))
        parser.add_argument(
            '--host', help='Etcd server host (Default: 127.0.0.1)', default="127.0.0.1")
        parser.add_argument(
            '--port', type=int, help='Etcd server port (Default: 4001)', default=4001)
        parser.add_argument(
            '--protocol', help='Etcd server protocol (Default: http)', default="http")
        parser.add_argument('cmd', nargs=argparse.REMAINDER)
        self._args = parser.parse_args()
        self.run()


def main():
    cmd = EtcdLockCmd()
    cmd.main()

if __name__ == "__main__":
    main()
