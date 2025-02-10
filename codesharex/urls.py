from django.urls import path
from . import views

urlpatterns = [
    path('add-content', views.add_content, name='add-content'),
    path('get-content', views.get_content, name='get-content'),
    path('update-content', views.update_content, name='update-content'),
    path('delete-content', views.delete_content, name='delete-content'),
    path('get-collect', views.get_collect, name='get-collect'),
    path('set-collect', views.set_collect, name='set-collect'),
    path('get-share', views.get_share, name='get-share'),
    path('get-openid', views.get_openid, name='get-openid'),
    path('get-user', views.get_user, name='get-user'),
    path('create-user', views.create_user, name='create-user'),
    path('update-user', views.update_user, name='update-user'),
    path('upload-avatar', views.upload_avatar, name='upload-avatar'),
    path('add-comment', views.add_comment, name='add-comment'),
    path('get-comment', views.get_comment, name='get-comment'),
    path('get-message', views.get_message, name='get-message'),
    path('delete-message', views.delete_message, name='delete-message'),
    path('read-message', views.read_message, name='read-message'),
    path('token', views.token, name='token'),
]
