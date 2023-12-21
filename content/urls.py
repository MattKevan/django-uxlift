from django.urls import path
from django.urls import re_path
from . import views  # Assuming you have views you want to map
from .views import PostListView, refresh_feeds_ajax, submit_post, topic_page
from .models import Post

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('submit/', views.submit_url, name='submit_url'),
    path('sites/', views.list_sites, name='list_sites'),
    path('refresh-feeds/', refresh_feeds_ajax, name='refresh-feeds-ajax'),
    path('submit-post/', submit_post, name='submit_post'),
    path('topics/', views.topics, name='topics'),
    path('topics/<slug:tag_slug>/', topic_page, name='topic_page'),
    path('tools/', views.tools, name='tools'),
    path('tools/<slug:tool_slug>/', views.tool_page, name='tool_page'),
    path('<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<slug:post_title_slug>/', views.post_view, name='post_view'),

]