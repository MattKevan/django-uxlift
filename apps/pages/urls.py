from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("about/", views.about, name="about"),
    path('topics/', views.topics, name='topics'),
    path("tools/", views.tools, name="tools"),
    path("news/", views.news, name="news"),
    path("sites/", views.sites, name="sites"),
    path("privacy/", views.privacy, name="privacy"),

]


