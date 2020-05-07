from django.test import TestCase, Client


class TestNotFound(TestCase):
    def setUp(self):
        self.client = Client()

    def test_page_not_fount(self):
        response = self.client.get("/some-testing-page/")
        self.assertEqual(response.status_code, 404)
