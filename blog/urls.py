from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
]
