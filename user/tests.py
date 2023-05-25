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


class VerifyEmailViewTest(APITestCase):
    # setUp 함수 : 테스트 코드 실행 전에 실행하겠다.(유저 생성)
    def setUp(self):            
        self.user = User.objects.create_user(email='sdgasdf@naver.com',
                                             account='admin',
                                             nickname='admin',
                                             password='G1843514dadg23@')

    # 이메일 인증 테스트 코드
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend") # 이메일을 실제로 전송하지 않고 로컬 메모리에 저장하는 백엔드
    def test_email_verification(self):
        token = PasswordResetTokenGenerator().make_token(self.user)
        uid = urlsafe_b64encode(force_bytes(self.user.pk))
        
        verification_link = f'http://localhost:8000/user/verify-email/{uid}/{token}/'  # 확인 링크를 가정합니다.
        response = self.client.get(verification_link)

        # self.assertEqual(response.status_code, 200)  # return Response 사용할 경우 : 확인 링크를 클릭하여 이메일 주소를 확인합니다.
        self.assertEqual(response.status_code, 302) # 302 리다이렉트 상태 코드
        self.assertRedirects(response, "http://127.0.0.1:5500/user/login.html", fetch_redirect_response=False)
        # fetch_redirect_response=False 외부 서비스나 다른 서버에서 제공될 경우 사용되며 원격 URL을 가져오지 않고, 상태코드와 리다이렉트 대상 URL에 집중하여 검증진행.

        self.user.refresh_from_db()  # 사용자 데이터 다시 불러오기
        self.assertTrue(self.user.is_active)  # 사용자가 활성화 상태인지 확인


class CustomTokenObtainPairViewTest(APITestCase):
    # setUp 함수 : 테스트 코드 실행 전에 실행하겠다.(유저 생성)
    def setUp(self):            
        self.user = User.objects.create_user(email='sdgasdf@naver.com',
                                             account='admin',
                                             nickname='admin',
                                             password='G1843514dadg23@')
        self.user.is_active = True # 활성화
        self.user.save()

    # 로그인 테스트 코드
    def test_login(self):
        url = reverse("login_view")
        login_data = {
            'account': 'admin',
            'password': 'G1843514dadg23@'
        }
        response = self.client.post(url, login_data)
        print(response.data)
        self.assertEqual(response.status_code, 200) # 로그인 요청이 성공적으로 처리되었는지 확인

    # 프로필 페이지 상세보기 테스트 코드
    def test_profil_detail(self):
        user_id = self.user.id # 프로필 페이지를 확인할 사용자의 user_id
        url = reverse("profile_view", kwargs={"user_id": user_id})
        
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 프로필 페이지 수정 테스트 코드
    def test_profil_update(self):
        user_id = self.user.id
        url = reverse("profile_view", kwargs={"user_id": user_id})
        update_data = {
            "nickname" : "nick",
            "introduce": "안녕하십니까!"
        }

        response = self.client.force_authenticate(user=self.user) # force_authenticate 인증된 사용자로 변경
        response = self.client.patch(url, update_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)