from base64 import urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.db.models.query_utils import Q
from django.core.mail import EmailMessage

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers, exceptions
from user.models import User
from user.validators import (
    password_validator,
    password_pattern,
    account_validator,
    nickname_validator,
)

import threading

from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    joined_at = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followings = serializers.StringRelatedField(many=True, required=False)
    followers = serializers.StringRelatedField(many=True, required=False)

    def get_joined_at(self, obj):
        return obj.joined_at.strftime("%Y년 %m월 %d일")

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.followings.count()

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "account": {
                "error_messages": {
                    "required": "ID는 필수 입력 사항입니다.",
                    "blank": "ID는 필수 입력 사항입니다.",
                }
            },
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호는 필수 입력 사항입니다.",
                    "blank": "비밀번호는 필수 입력 사항입니다.",
                },
            },
            "email": {
                "error_messages": {
                    "required": "email은 필수 입력 사항입니다.",
                    "invalid": "email 형식이 맞지 않습니다. 알맞은 형식의 email을 입력해주세요.",
                    "blank": "email은 필수 입력 사항입니다.",
                }
            },
            "nickname": {
                "error_messages": {
                    "required": "nickname은 필수 입력 사항입니다.",
                    "invalid": "nickname 형식이 맞지 않습니다. 알맞은 형식의 nickname을 입력해주세요.",
                    "blank": "nickname은 필수 입력 사항입니다.",
                }
            },
            "is_admin": {
                "write_only": True,
            },
            "is_active": {
                "write_only": True,
            },
        }

    def validate(self, data):
        account = data.get("account")
        password = data.get("password")
        nickname = data.get("nickname")

        # 아이디 유효성 검사
        if account_validator(account):
            raise serializers.ValidationError(
                detail={"username": "아이디는 5자 이상 20자 이하의 숫자, 영문 대/소문자를 포함하여야 합니다."}
            )

        # 비밀번호 유효성 검사
        if password_validator(password):
            raise serializers.ValidationError(
                detail={"password": "비밀번호는 8자 이상의 영문 대/소문자와 숫자, 특수문자를 포함하여야 합니다."}
            )

        # 비밀번호 유효성 검사
        if password_pattern(password):
            raise serializers.ValidationError(
                detail={"password": "비밀번호는 연속해서 3자리 이상 동일한 영문,숫자,특수문자 사용이 불가합니다."}
            )
            
        if nickname_validator(nickname):
            raise serializers.ValidationError(
                detail={"nickname": "닉네임은 공백 없이 2자이상 8자 이하의 영문, 한글,'-' 또는'_'만 사용 가능합니다."}
            )

        return data

    # 회원가입
    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    # def update(self, instance, validated_data):
    #     user = super().update(instance, validated_data)
    #     password = user.password
    #     user.set_password(password)
    #     user.save()
    #     return user


# 회원정보 수정 serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("nickname", "profile_img", "introduce")
        extra_kwargs = {
            "nickname": {
                "error_messages": {
                    "required": "닉네임을 입력해주세요.",
                    "blank": "닉네임을 입력해주세요.",
                }
            },
        }

    def validate(self, data):
        nickname = data.get("nickname")

        # 닉네임 유효성 검사
        if nickname_validator(nickname):
            raise serializers.ValidationError(
                detail={"닉네임은 공백 없이 2자이상 8자 이하의 영문, 한글,'-' 또는'_'만 사용 가능합니다."}
            )

        return data

    # def create(self, validated_data):
    #     user = super().create(validated_data)
    #     password = user.password
    #     user.set_password(password)
    #     user.save()
    #     return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)

        user.save()
        return user


# 로그인 토큰 serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["account"] = user.account
        token["nickname"] = user.nickname
        token["point"] = user.point
        token["profile_img"] = str(user.profile_img)
        return token

    def get_user(self, validated_data):
        user = self.user
        return user


# ===========================================================
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(
            subject=message["email_subject"],
            body=message["email_body"],
            to=[message["to_email"]],
        )
        EmailThread(email).start()


# ===========================================================


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
            absurl = f"http://{frontend_site}/user/set_password.html?id=${uidb64}&token=${token}"

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
                detail={"email": "잘못된 이메일입니다. 다시 입력해주세요."}
            )


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
                    detail={"repassword": "비밀번호가 일치하지 않습니다."}
                )
            # 비밀번호 유효성 검사
            if password_validator(password):
                raise serializers.ValidationError(
                    detail={"password": "비밀번호는 8자 이상의 영문 대/소문자와 숫자, 특수문자를 포함하여야 합니다."}
                )

            # 비밀번호 유효성 검사
            if password_pattern(password):
                raise serializers.ValidationError(
                    detail={"password": "비밀번호는 연속해서 3자리 이상 동일한 영문,숫자,특수문자 사용이 불가합니다."}
                )

            user.set_password(password)
            user.save()

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(detail={"user": "존재하지 않는 회원입니다."})


# User Token 획득
class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )


# 회원탈퇴 serializer
class UserDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_active",)


# 비밀번호 확인
class PasswordVerificationSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)


# 팔로우/팔로워
class FollowSerializer(serializers.ModelSerializer):
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    def get_followings(self, obj):
        followings = obj.followings.all()
        return [
            {
                "nickname": following.nickname,
                "id": following.id,
                "profile_image": self.get_profile_image_url(following.profile_img),
            }
            for following in followings
        ]

    def get_followers(self, obj):
        followers = obj.followers.all()
        return [
            {
                "nickname": follower.nickname,
                "id": follower.id,
                "profile_image": self.get_profile_image_url(follower.profile_img),
            }
            for follower in followers
        ]

    def get_profile_image_url(self, profile_img):
        if profile_img:
            return f"{settings.MEDIA_URL}{profile_img}"
        return None

    class Meta:
        model = User
        fields = ["followings", "followers"]
