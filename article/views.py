from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from .models import Articles, Comments
from rest_framework import permissions
from .serializers import (
    CommentsSerializer,
    CommentsCreateSerializer)

class CommentsView(APIView):
    # ===================== 댓글 목록 보기 =========================
    def get(self, article_id):
        article = get_object_or_404(Articles, id=article_id)
        comments = article.comments.all()
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ======================== 댓글 작성 ============================
    def post(self, request, article_id):
        serializer = CommentsCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, article_id=article_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    # ======================== 댓글 삭제 ============================
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comments, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({"message": "삭제완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "댓글 작성자만 삭제 가능."}, status=status.HTTP_403_FORBIDDEN)