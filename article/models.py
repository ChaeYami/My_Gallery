from django.db import models
from user.models import User
import os
from uuid import uuid4
from datetime import date


# 이미지 파일 이름 uuid형식으로 바꾸기
def rename_imagefile_to_uuid(instance, filename):
    now = date.today()
    upload_to = f"article/{now.year}/{now.month}/{now.day}/{instance}"
    ext = filename.split(".")[-1]
    uuid = uuid4().hex

    if instance:
        filename = "{}_{}.{}".format(uuid, instance, ext)
    else:
        filename = "{}.{}".format(uuid, ext)
    return os.path.join(upload_to, filename)


class Article(models.Model):
    class Meta:
        db_table = "Article"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    title = models.CharField(max_length=50, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    hearts = models.ManyToManyField(User, blank=True, related_name="hearts")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성시간")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정시간")

    # ---------------- 좋아요 갯수 ----------------
    def count_hearts(self):
        return self.hearts.count()

    # 이미지
    uploaded_image = models.ImageField(
        upload_to=rename_imagefile_to_uuid, verbose_name="업로드이미지"
    )
    changed_image = models.ImageField(
        upload_to=rename_imagefile_to_uuid, verbose_name="변환된이미지"
    )

    def __str__(self):
        return str(self.title)


# 댓글 models
class Comment(models.Model):
    class Meta:
        db_table = "comment"
        ordering = ["-comment_created_at"]  # 댓글 최신순 정렬

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comment"
    )
    comment = models.TextField("댓글")
    comment_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.comment)
