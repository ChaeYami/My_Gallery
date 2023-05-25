from django.urls import path
from . import views

urlpatterns = [
    path("<int:change_id>/", views.TransformView.as_view(), name="transform_view"),
]
