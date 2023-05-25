from rest_framework import serializers
from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_created_at = serializers.DateTimeField(
        format="%y-%m-%d %H:%M", read_only=True
    )

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "pk": obj.user.pk}

    class Meta:
        model = Comment
        exclude = ("article",)  # 게시글 필드 빼고 보여주기


# comments작성
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
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
        return {"nickname": obj.user.nickname, "id": obj.user.id}

    class Meta:
        model = Article
        fields = ["id", "title", "user", "changed_image", "hearts"]
