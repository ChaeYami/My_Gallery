from django.urls import path
from article import views


urlpatterns = [
    path("", views.ArticleView.as_view(), name="article_view"),
    path("<int:article_id>/", views.ArticleDetailView.as_view(),name="article_detail_view",),
    
    path('<int:article_id>/hearts/', views.ArticleHeartsView.as_view(),name='Hearts_view'),  # 좋아요 기능
    path('hearts/<int:user_id>', views.HeartsListView.as_view(),name='User_Hearts_View'),  # 좋아요 한 게시글
    
    path("<int:article_id>/comment/", views.CommentView.as_view(), name="comment_view"),
    path("comment/<int:comment_id>/", views.CommentView.as_view(), name="comment_delete"),
    
    path('list/<int:user_id>/', views.ArticleListView.as_view(), name='article_list'),  # /article/<int:article_id>/list
]
