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


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    uploaded_image = serializers.ImageField()
    changed_image = serializers.ImageField()

    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Article
        fields = "__all__"


class ArticleCreateSerializer(serializers.ModelSerializer):
    uploaded_image = serializers.ImageField()
    changed_image = serializers.ImageField()

    class Meta:
        model = Article
        fields = ["title", "content", "uploaded_image", "changed_image"]


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    changed_image = serializers.ImageField()

    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Article
        fields = ["id", "title", "user", "changed_image"]

