from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, override_settings
from django.test import override_settings
from user.models import User
from base64 import urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, smart_bytes

# Create your tests here.
class SignupViewTest(APITestCase):
    # 회원가입 테스트 코드
    def test_signup(self):
        url = reverse("sign_up_view")
        data = {"email" : "sdgasdf@naver.com",
                "account" : "SHGDF",
                "nickname" : "test1",
                "password" : "G1843514dadg23!4"
                }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 201)


