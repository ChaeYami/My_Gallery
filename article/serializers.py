from rest_framework import serializers
from .models import Article, Comments

class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_created_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    comment_updated_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}

    class Meta:
        model = Comments
        exclude = ('article',)  # 게시글 필드 빼고 보여주기


# comments작성
class CommentsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ("comment",)