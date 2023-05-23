from rest_framework import serializers
from article.models import Article


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
