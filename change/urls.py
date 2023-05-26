from django.urls import path
from . import views

urlpatterns = [
    path("", views.TransformView.as_view(), name="transform_view"),
]
