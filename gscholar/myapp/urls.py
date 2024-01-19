from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("articles", views.articles, name="articles"),
]
