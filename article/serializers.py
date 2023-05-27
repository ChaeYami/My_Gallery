from rest_framework import serializers
from .models import Article, Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_created_at = serializers.DateTimeField(
        format="%y-%m-%d %H:%M", read_only=True
    )

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "pk": obj.user.pk,"profile_img": str(obj.user.profile_img)}

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
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True
    )
    # id = serializers.IntegerField()  # 'id' 필드 추가(테스트 코드)
    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "pk": obj.user.pk,"profile_img": str(obj.user.profile_img)} # 닉네임 사용해야 함
        # return obj.user.id
    class Meta:
        model = Article
        fields = "__all__"


# 테스트 코드 에러 주석 처리
class ArticleCreateSerializer(serializers.ModelSerializer):
    uploaded_image = serializers.ImageField()
    changed_image = serializers.ImageField()

    class Meta:
        model = Article
        fields = ["title", "content", "uploaded_image", "changed_image", "change_id"]
        


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    changed_image = serializers.ImageField()

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "id": obj.user.id, "profile_img": str(obj.user.profile_img)}

    class Meta:
        model = Article
        fields = ["id", "title", "user", "changed_image", "hearts"]