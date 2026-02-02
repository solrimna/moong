from django.urls import re_path
from . import views

app_name = 'users'

urlpatterns = [
    re_path(r"^signup/$", views.signup_view, name="signup"),
    re_path(r'^mypage/$', views.mypage, name='mypage'),                             # /users/mypage/
    re_path(r'^mypage/edit/$', views.mypage_edit, name='mypage_edit'),                  # /users/mypage/edit/
    re_path(r'^mypage/activity/$', views.mypage_activity, name='mypage_activity'),         # /users/mypage/activity/
    re_path(r'^profile/(?P<user_id>\d+)/$', views.user_profile, name='user_profile'),         # /users/profile/사용자id숫자
    re_path(r"^login/$", views.login_view, name="login"),
    re_path(r"^logout/$", views.logout_view, name="logout"),
    re_path(r'^mypage/created/$', views.mypage_created_list, name='mypage_created_list'),           # 추가 ✅
    re_path(r'^mypage/participated/$', views.mypage_participated_list, name='mypage_participated_list'),  # 추가 ✅
]