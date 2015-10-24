import unittest
import time
import etcd
from threading import Thread
from etcdlock.etcdlock import EtcdLock


class TestEtcdLock(unittest.TestCase):

    def setUp(self):
        self._thread_value = None
        self._etcdlock = EtcdLock(key="key", id="id")
        try:
            self._etcdlock._client.delete("key")
        except:
            pass

    def test_same_id_reacquires_lock(self):
        self._etcdlock._client.write("key", "id")
        self._etcdlock.acquire()

        self.assertEquals("id", self._etcdlock._client.read("key").value)

    def test_on_key_not_found_acquire_lock(self):
        self._etcdlock.acquire()

        self.assertEquals("id", self._etcdlock._client.read("key").value)

    def test_with_statement(self):
        with self._etcdlock:
            self.assertEquals("id", self._etcdlock._client.read("key").value)
        self.assertRaises(etcd.EtcdKeyNotFound, lambda: self._etcdlock._client.read("key"))

    def test_block_others_until_done(self):
        self._etcdlock.acquire()
        Thread(target=lambda: self.__second_client()).start()
        time.sleep(1)
        self.assertIsNone(self._thread_value)
        self._etcdlock.release()
        time.sleep(1)
        self.assertEqual("done", self._thread_value)

    def __second_client(self):
        with EtcdLock(key="key", id="id2"):
            self._thread_value = "done"
