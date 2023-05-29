from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from article.models import Article, Comment
from article.serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)
from user.models import User

from django.db.models import Count


class ArticleView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        articles = Article.objects.all().order_by("-created_at")
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleCreateSerializer(article, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            article.delete()
            return Response({"message": "삭제완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)


# =================== 글 리스트 목록 ===================


class ArticleListView(APIView):  # /article/list/<int:user_id>/
    def get(self, request, user_id):  # => request.method == 'GET':
        articles = Article.objects.filter(user_id=user_id)
        serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ===================== 댓글 목록 보기 =========================
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        comments = article.comment.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ======================== 댓글 작성 ============================
    def post(self, request, article_id):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, article_id=article_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ======================== 댓글 삭제 ============================
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({"message": "삭제완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"message": "댓글 작성자만 삭제 가능."}, status=status.HTTP_403_FORBIDDEN
            )


# ------------------- 게시글 좋아요 -------------------
class ArticleHeartsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)

        if request.user in article.hearts.all():
            article.hearts.remove(request.user)
            return Response({"message": "좋아요를 취소했습니다."}, status=status.HTTP_200_OK)
        else:
            article.hearts.add(request.user)
            return Response({"message": "좋아요를 눌렀습니다."}, status=status.HTTP_200_OK)

    # ------------------- 게시글 좋아요 갯수 -------------------
    def get(self, request, article_id):
        article = Article.objects.get(id=article_id)
        heart_count = article.count_hearts()
        return Response({"hearts": heart_count})


class HeartsListView(APIView):
    # --------------------- 게시글 좋아요/취소 ----------------------
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)

        if request.user in article.hearts.all():
            article.hearts.remove(request.user)
            return Response("좋아요 취소", status=status.HTTP_200_OK)
        else:
            article.hearts.add(request.user)
            return Response("좋아요", status=status.HTTP_200_OK)

    def get(self, request, user_id=None):
        if user_id is None:
            #----------------- 좋아요 순위 ----------------- 
            # 게시글을 좋아요 수를 기준으로 정렬
            article = Article.objects.annotate(hearts_count=Count('hearts')).order_by('-hearts_count')
            # 필요한 정보를 추출하여 리스트에 저장
            rank_list = []
            for index, article in enumerate(article[:5]):  # 상위 5개 게시글만 
                rank_item = {
                    'rank': index + 1,
                    'author': article.user.nickname,
                    'title': article.title,
                    'hearts': article.hearts_count, # 좋아요 수
                    'article_id': article.id,
                }
                rank_list.append(rank_item)
            return Response(rank_list, status=status.HTTP_200_OK)
        else:
            #----------------- 좋아요 게시글 보기 ----------------- 
            user = User.objects.get(id=user_id)
            article = user.hearts.all()
            serializer = ArticleSerializer(article, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


