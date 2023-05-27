from base64 import urlsafe_b64decode, urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import DjangoUnicodeDecodeError, force_str, force_bytes
from django.shortcuts import redirect
from django.core.mail import EmailMessage

from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView

from user.serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserDelSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    TokenSerializer,
    EmailThread,
    PasswordVerificationSerializer,
    UserUpdateSerializer,
    FollowSerializer,
)

from .models import User


# ================================ 회원가입 시작 ================================
class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(
            subject=message["email_subject"],
            body=message["email_body"],
            to=[message["to_email"]],
        )
        EmailThread(email).start()


# 가입 클릭 시 이메일 전송
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        # try:
        #     User.objects.get(email=email)
        #     return Response({"message":"이미 존재하는 사용자의 이메일입니다.."},status=status.HTTP_400_BAD_REQUEST)
        # except:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # 토큰 생성
            uid = urlsafe_b64encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            # 이메일 전송
            email = user.email
            authurl = f"http://localhost:8000/user/verify-email/{uid}/{token}/"
            email_body = "이메일 인증" + authurl
            message = {
                "email_body": email_body,
                "to_email": email,
                "email_subject": "이메일 인증",
            }
            Util.send_email(message)

            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


# 이메일 인증
class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            # URL에 포함된 uid를 디코딩하여 사용자 식별
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        # 사용자가 존재하고 토큰이 유효한지 확인
        if user is not None and token_generator.check_token(user, token):
            # 이메일 인증 완료 처리 - 유저 활성화
            user.is_active = True
            user.save()
            # return Response({"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)
            return redirect("http://127.0.0.1:5500/user/login.html")
        else:
            return Response(
                {"message": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST
            )


# ================================ 회원가입 끝 ================================


# ================================ 로그인 ================================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ================================ 프로필 페이지 시작 ================================
class ProfileView(APIView):
    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)

    # 프로필 페이지
    def get(self, request, user_id):
        user = self.get_object(user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 프로필 수정
    def patch(self, request, user_id):
        user = self.get_object(user_id)
        if user == request.user:
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

    # 회원 탈퇴 (비밀번호 받아서)
    def delete(self, request, user_id):
        user = self.get_object(user_id)
        datas = request.data
        datas["is_active"] = False
        serializer = UserDelSerializer(user, data=datas)
        if user.check_password(request.data.get("password")):
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "계정 비활성화 완료"}, status=status.HTTP_204_NO_CONTENT
                )
        else:
            return Response(
                {"message": f"패스워드가 다릅니다"}, status=status.HTTP_400_BAD_REQUEST
            )


# ================================ 프로필 페이지 끝 ================================


# ================================ 비밀번호 재설정 시작 ================================


# 이메일 보내기
class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 이메일"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 재설정 토큰 확인
class PasswordTokenCheckView(APIView):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_b64decode(uidb64))
            user = get_object_or_404(User, id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED
                )

            return Response(
                {"uidb64": uidb64, "token": token}, status=status.HTTP_200_OK
            )

        except DjangoUnicodeDecodeError as identifier:
            return Response(
                {"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


# 비밀번호 재설정
class SetNewPasswordView(APIView):
    def put(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 회원정보 인증 토큰 발급
class ObtainUserTokenView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================ 비밀번호 재설정 끝 ================================


# ================================ 팔로우 시작 ================================
class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 팔로우 등록/취소
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if you != me:
            if me in you.followers.all():
                you.followers.remove(me)
                return Response("unfollow", status=status.HTTP_205_RESET_CONTENT)
            else:
                you.followers.add(me)
                return Response("follow", status=status.HTTP_200_OK)
        else:
            return Response("자신을 팔로우 할 수 없습니다.", status=status.HTTP_403_FORBIDDEN)

    # 팔로우/팔로워 리스트
    def get(self, request, user_id):
        followings = User.objects.filter(id=user_id)
        serializer = FollowSerializer(followings, many=True)
        return Response(serializer.data)


# ================================= 팔로우 끝 =================================


# 계정 재활성화
class ActivateAccountView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email, is_active=False)
            # 유저가 비활성화된 상태인 경우에만 계정을 활성화할 수 있도록 검증합니다.
            uid = urlsafe_b64encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            authurl = f"http://localhost:8000/user/verify-email/{uid}/{token}/"
            email_body = "계정 재활성화를 위한 이메일 인증 링크입니다. " + authurl
            message = {
                "email_body": email_body,
                "to_email": email,
                "email_subject": "계정 재활성화 이메일 인증",
            }
            Util.send_email(message)
            return Response(
                {"message": "이메일을 통해 계정 재활성화 링크가 전송되었습니다."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "비활성화된 상태가 아닌 계정입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
