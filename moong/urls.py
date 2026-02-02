from django.urls import re_path
from . import views

app_name = 'moong'

urlpatterns = [
    re_path(r'^post/add/$', views.post_form, name='post_add'),
    re_path(r'^post/add/confirm/$', views.post_add_confirm, name='post_add_confirm'),  
    re_path(r'^post/(?P<post_id>\d+)/$', views.post_detail, name='post_detail'),
    re_path(r'^post/(?P<post_id>\d+)/edit/$', views.post_form, name='post_mod') ,
    re_path(r'^post/(?P<post_id>\d+)/delete/$', views.post_delete, name='post_delete'),
    re_path(r'^post/(?P<post_id>\d+)/closed/$', views.post_closed_toggle, name='post_closed'),
    re_path(r'^post/(?P<post_id>\d+)/closed_cancel/$', views.post_closed_toggle, name='post_closed_cancel'),   
    re_path(r'^post/(?P<post_id>\d+)/finished/$', views.moim_finished, name='moim_finished'),   
    re_path(r'^tags/(?P<tag_name>[^/]+)/$', views.tag_feeds, name='tag_feeds'),
    re_path(r'^$', views.main, name='main'),
    re_path(r'^post/(?P<post_id>\d+)/apply/$', views.participation_apply, name='participation_apply'),
    re_path(r'^post/(?P<post_id>\d+)/cancel/$', views.participation_cancel, name='participation_cancel'),
    re_path(r'^post/(?P<post_id>\d+)/comment/add/$', views.comment_add, name='comment_add'),
    re_path(r'^comment/(?P<comment_id>\d+)/delete/$', views.comment_delete, name='comment_delete'),
    re_path(r'^participation/(?P<participation_id>\d+)/manage/', views.participation_manage, name='participation_manage'),

    re_path(r'^ddomoong/(?P<participation_id>\d+)/$', views.give_ddomoong, name='give_ddomoong'),
]