from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):

    def create_user(self, account, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have a email")

        user = self.model(
            account=account,
            email=self.normalize_email(email),  # 소문자로 바꾼 후 정규화 체크
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,

            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        db_table = "User"

    account = models.CharField("아이디", max_length=20, unique=True)
    email = models.EmailField("이메일",max_length=255, unique=True)
    nickname = models.CharField("닉네임", max_length=15)
    profile_img = models.ImageField("프로필사진",blank=True,)
   
    followings = models.ManyToManyField("self", symmetrical=False, related_name='followers', blank=True)

    is_active = models.BooleanField("활성화", default=False) # 이메일 인증 전에는 비활성화
    is_staff = models.BooleanField("스태프", default=False)
    is_admin = models.BooleanField("관리자", default=False)

    objects = UserManager()
    USERNAME_FIELD = 'account'
    REQUIRED_FIELDS = ["email",]

    def __str__(self):
        return self.account

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    
    
# class CheckEmail(models.Model):
#     email = models.EmailField("이메일", max_length=255, unique=True,)
#     random_num=models.IntegerField()
#     try_num = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
