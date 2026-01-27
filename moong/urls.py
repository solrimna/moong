from django.urls import re_path
from . import views

app_name = 'moong'

urlpatterns = [
    re_path(r'^post/add/$', views.post_add, name='post_add'),
    re_path(r'^post/(?P<post_id>\d+)/$', views.post_detail, name='post_detail'),
    re_path(r'^$', views.post_list, name='post_list'),
]