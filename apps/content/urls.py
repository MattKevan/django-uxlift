from django.urls import path
from django.urls import re_path
from . import views  
from .models import Post

urlpatterns = [
    path('submit/', views.submit_url, name='submit_url'),
    path('submit-post/', views.submit_post, name='submit_post'),
    path('topics/<slug:topic_slug>/', views.topic_page, name='topic_page'),
    path('tools/<slug:tool_slug>/', views.tool_page, name='tool_page'),
    path('<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<slug:post_title_slug>/', views.post_view, name='post_view'),
    path('post/<int:post_id>/unpublish/', views.unpublish_post, name='unpublish_post'),

]