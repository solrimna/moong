from django.urls import re_path
from . import views

app_name = 'moong'

urlpatterns = [
    re_path(r'^post/add/$', views.post_add, name='post_add'),
    re_path(r'^post/(?P<post_id>\d+)/$', views.post_detail, name='post_detail'),
    re_path(r'^post/(?P<post_id>\d+)/edit/$', views.post_mod, name='post_mod') ,
    re_path(r'^post/(?P<post_id>\d+)/delete/$', views.post_delete, name='post_delete'),
    re_path(r'^post/(?P<post_id>\d+)/closed/$', views.post_closed, name='post_closed'),   
    re_path(r'^post/(?P<post_id>\d+)/finished/$', views.moim_finished, name='moim_finished'),   
    re_path(r'^tags/(?P<tag_name>[^/]+)/$', views.tag_feeds, name='tag_feeds'),
    re_path(r'^$', views.main, name='main'),
    re_path(r'^post/(?P<post_id>\d+)/apply/$', views.post_apply, name='post_apply'),
    re_path(r'^post/(?P<post_id>\d+)/cancel/$', views.post_cancel, name='post_cancel'),
    re_path(r'^post/(?P<post_id>\d+)/comment/add/$', views.comment_add, name='comment_add'),
    re_path(r'^comment/(?P<comment_id>\d+)/delete/$', views.comment_delete, name='comment_delete'),
]