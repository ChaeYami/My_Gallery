from django.db import models
from user.models import Users

# 댓글 models
class Comments(models.Model):
    class Meta:
        db_table = 'comment'
        ordering = ['-comment_created_at']  # 댓글 최신순 정렬

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField("댓글")
    comment_created_at = models.DateTimeField(auto_now_add=True)
    comment_updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.comment)
