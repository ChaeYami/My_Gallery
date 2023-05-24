from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User

# Create your tests here.
class UserSingUpTest(APITestCase):
    def test_registration(self):
        url = reverse("sign_up_view")
        user_data = {
            "email" : "sngffd@naver.com",
            "account" : "asdgwe",
            "nickname" : "test1",
            "password" : "G1843514dadg23!4"
            }
        response = self.client.post(url, user_data)
        print(response.data)
        self.assertEqual(response.status_code, 201)


