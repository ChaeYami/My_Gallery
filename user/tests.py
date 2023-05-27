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
        url = reverse("user:sign_up_view")
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

    # 생성한 유저 활성화 확인 테스트 코드    
    def test_create_user_is_active(self):
        self.assertFalse(self.user.is_active)

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
        url = reverse("user:login_view")
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
        url = reverse("user:profile_view", kwargs={"user_id": user_id})
        
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 프로필 페이지 수정 테스트 코드
    def test_profil_update(self):
        user_id = self.user.id
        url = reverse("user:profile_view", kwargs={"user_id": user_id})
        update_data = {
            "nickname" : "nick",
            "introduce": "안녕하십니까!"
        }

        response = self.client.force_authenticate(user=self.user) # force_authenticate 인증된 사용자로 변경
        response = self.client.patch(url, update_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 회원 탈퇴 테스트 코드
    def test_user_delete(self):
        user_id = self.user.id
        url = reverse("user:profile_view", kwargs={"user_id": user_id})
        delete_data = {
            "password": "G1843514dadg23@"
        }        

        response = self.client.delete(url, data=delete_data)
        print(response.data)
        self.assertEqual(response.status_code, 204)


class FollowViewTest(APITestCase):        
    def setUp(self):            
            self.user = User.objects.create_user(email='sdgasdf@naver.com', account='admin', nickname='admin', password='G1843514dadg23@')
            self.user_1 = User.objects.create_user(email='adgdsa@naver.com', account='badf', nickname='adasdfmin', password='G184351dsa4dadg23@')
            self.user_2 = User.objects.create_user(email='asdgbvds@naver.com', account='admadsbvsain', nickname='adewrfmin', password='G184351fd4dadg23@')
            self.user_3 = User.objects.create_user(email='sadg@naver.com', account='eqwr', nickname='asdg', password='G184351f@!$g23@')

            self.user.followings.add(self.user_1, self.user_2)  # self.user가 팔로우 진행
            self.user.followers.add(self.user_1, self.user_2) # self.user를 팔로우 진행

            self.client.force_authenticate(user=self.user) # force_authenticate 인증된 사용자로 로그인

    # 팔로우 등록 실패(나 자신 팔로우 진행) 테스트 코드
    def test_follow_fail(self):
        user_id = self.user.id
        url = reverse("user:follow_view", kwargs={"user_id": user_id})
        response = self.client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, 403)

    # 팔로우 등록 테스트 코드
    def test_follow(self):
        user_id = self.user_3.id
        url = reverse("user:follow_view", kwargs={"user_id": user_id})
        response = self.client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 팔로우 취소 테스트 코드
    def test_follow_cancel(self):
        user_id = self.user_2.id
        url = reverse("user:follow_view", kwargs={"user_id": user_id})
        response = self.client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, 205)

    # 팔로우/팔로잉 리스트 보기 테스트 코드
    def test_follow_list(self):
        user_id = self.user.id # 확인할 팔로우 페이지의 사용자 id
        url = reverse("user:follow_view", kwargs={"user_id": user_id})
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)


class PasswordResetViewTest(APITestCase):
    def setUp(self):            
        self.user = User.objects.create_user(email='sdgasdf@naver.com', account='admin', nickname='admin', password='G1843514dadg23@')
        self.client.force_authenticate(user=self.user) # force_authenticate 인증된 사용자로 로그인
        self.token = PasswordResetTokenGenerator().make_token(self.user) # token값 발급
        self.uidb64 = urlsafe_b64encode(smart_bytes(self.user.id)).decode() # uidb64값 발급

    # 비밀번호 재설정 이메일 보내기 테스트 코드
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_email_send(self):
        url = reverse("user:password_reset")
        password_reset_data = {'email' : 'sdgasdf@naver.com'}
        response = self.client.post(url, password_reset_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 비밀번호 재설정 토큰 확인 테스트 코드    
    def test_password_token_check(self):      
        url = reverse("user:password_reset_confirm", kwargs={"token": self.token, "uidb64" : self.uidb64})
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 비밀번호 재설정 테스트 코드
    def test_set_new_password(self):
        url = reverse("user:password_reset_confirm")
        new_password_data = {
                "password": "qEadg423$#hbnad",
                "repassword": "qEadg423$#hbnad",
                "token": self.token,
                "uidb64": self.uidb64
        }
        response = self.client.put(url, new_password_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    
class ActivateAccountViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='sdgasdf@naver.com', account='admin', nickname='admin', password='G1843514dadg23@')
        self.user.is_active = False # 계정 비활성화일 경우에 진행을 위해 정보 추가
        self.user.save()

    # 계정 재활성화 이메일 전송 확인 테스트 코드
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_reactivate_account_email_send(self):           
        url = reverse("user:reactivation")
        reactivate_data = {'email':'sdgasdf@naver.com'}

        response = self.client.post(url, reactivate_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 계정 재활성화 이메일 인증 테스트 코드
    def test_reactivate_account(self):
        uid = urlsafe_b64encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        authurl_link = f"http://localhost:8000/user/verify-email/{uid}/{token}/"
        
        response = self.client.get(authurl_link)
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db() # 데이터 베이스 업데이트
        self.assertTrue(self.user.is_active) # 계정 활성화 True 확인