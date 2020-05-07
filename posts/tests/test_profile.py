from django.test import TestCase, Client
from django.shortcuts import reverse as rv

# Create your tests here.

class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()

    def test_profile_page(self):

        response = self.client.get(
                    rv("profile", kwargs={"username": "testuser"})
                )
        self.assertEqual(response.status_code, 404)

        self.client.post(
                    rv("signup"),
                    {
                        "username": "testuser",
                        "email": "testuser@yandex.ru",
                        "password1": "aFASfaf124124",
                        "password2": "aFASfaf124124"
                    }
                )

        response = self.client.get(
                    rv("profile", kwargs={"username": "testuser"})
                )
        self.assertEqual(response.status_code, 200)


