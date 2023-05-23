from base64 import urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.db.models.query_utils import Q
from django.core.mail import EmailMessage

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers, exceptions
from user.models import User

import threading

from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("followings",)
        extra_kwargs = {
            "password":{
                "write_only":True,
            },
            "is_admin":{
                "write_only":True,
            },
            "is_active":{
                "write_only":True,
            }
        }
        
    # 회원가입
    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user
    
    # 로그인
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("nickname","profile_img","introduce")

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user
    
    def update(self,instance, validated_data):
        user = super().update(instance,validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['account'] = user.account
        token['nickname'] = user.nickname
        return token


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:

    @staticmethod
    def send_email(message):
        email = EmailMessage(subject=message["email_subject"], body=message["email_body"], to=[
                             message["to_email"]])
        EmailThread(email).start()


# 비밀번호 찾기 serializer
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        try:
            email = attrs.get("email")

            user = User.objects.get(email=email)
            uidb64 = urlsafe_b64encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            frontend_site = "127.0.0.1:5500"
            absurl = f"http://{frontend_site}/set_password.html?id=${uidb64}&token=${token}"

            email_body = "비밀번호 재설정 \n " + absurl
            message = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "비밀번호 재설정",
            }
            Util.send_email(message)

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                detail={"email": "잘못된 이메일입니다. 다시 입력해주세요."})


# 비밀번호 재설정 serializer
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
    )
    repassword = serializers.CharField(
        write_only=True,
    )
    token = serializers.CharField(
        max_length=100,
        write_only=True,
    )
    uidb64 = serializers.CharField(
        max_length=100,
        write_only=True,
    )

    class Meta:
        fields = (
            "repassword",
            "password",
            "token",
            "uidb64",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        repassword = attrs.get("repassword")
        token = attrs.get("token")
        uidb64 = attrs.get("uidb64")

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if PasswordResetTokenGenerator().check_token(user, token) == False:
                raise exceptions.AuthenticationFailed("토큰이 유효하지 않습니다.", 401)
            if password != repassword:
                raise serializers.ValidationError(
                    detail={"repassword": "비밀번호가 일치하지 않습니다."})

            user.set_password(password)
            user.save()

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                detail={"user": "존재하지 않는 회원입니다."})


# 비밀번호 재설정 serializer
# class UserUpdatePasswordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("nickname","password","profile_img",)

#     def create(self, validated_data):
#         user = super().create(validated_data)
#         password = user.password
#         user.set_password(password)
#         user.save()
#         return user
    
#     def update(self,instance, validated_data):
#         user = super().update(instance,validated_data)
#         password = user.password
#         user.set_password(password)
#         user.save()
#         return user

class UserDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_active",)


# User Token 획득
class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )



class UserProfileSerializer(serializers.ModelSerializer):
    followings = serializers.StringRelatedField(many=True)
    followers = serializers.StringRelatedField(many=True)
    # articles_count = ArticlesSerializer  # 작성한 게시글
    # hearted_articles_count = serializers.SerializerMethodField()  # 내가 하트한 수

    profile_img = serializers.ImageField(
        max_length=None,
        use_url=True,
        required=False,  # 입력값이 없어도 유효성 검사를 통과
    )

    def get_hearted_count(self, obj):
        return obj.hearts.count()

    def clean_img(self):
        img = self.cleaned_data.get('profile_img')
        if img and img.size > 2 * 1024 * 1024:  # 2mb
            raise serializers.ValidationError('이미지 크기는 최대 2mb까지 가능해요.')
        return img
    class Meta:
        model = User
        fields = ("account", "nickname","email", "profile_img","followings","followers","hearted_count")


class UserDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_active",)


# 비밀번호 확인
class PasswordVerificationSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)