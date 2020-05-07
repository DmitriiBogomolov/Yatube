from django.test import TestCase, Client
from django.shortcuts import reverse as rv
from django.core.cache.backends import locmem


class TestCache(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_cache(self):
        self.assertFalse(locmem._caches[''])
        self.client.get(rv("index"))
        self.assertTrue(locmem._caches[''])
