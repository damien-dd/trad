from django.urls import path, re_path, include
from django.shortcuts import redirect

from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('done/', views.done, name='done'),
	path('todo/', views.todo, name='todo'),
	path('channels/', views.channels, name='channels'),
	path('tools/', views.tools, name='tools'),
	path('register/', views.register, name='register'),
	path('register/verify/<int:userId>/<str:token>/', views.email_confirm, name='email_confirm'),
	path('channel/', views.edit_channel, name='edit_channel'),
	path('suggest/', views.add_video, name='add_video'),
	path('video/<int:vidId>/', views.video, name='video'),
	path('video/<int:vidId>/vote/up/', views.video_vote_add, name='video_vote_add'),
	path('video/<int:vidId>/vote/down/', views.video_vote_remove, name='video_vote_remove'),
	path('video/<int:vidId>/subtitle/<int:fileId>/delete', views.video_subtitle_delete, name='video_subtitle_delete'),
	path('video/<int:vidId>/transcript/<int:fileId>/delete', views.video_transcript_delete, name='video_transcript_delete'),
	path('video/<int:vidId>/comment/<int:commentId>/delete', views.video_comment_delete, name='video_comment_delete'),
	path('theme/<str:filename>/', views.theme, name='theme'),
]

