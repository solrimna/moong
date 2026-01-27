from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^sido/", views.get_sido),
    re_path(r"^sigungu/", views.get_sigungu),
    re_path(r"^eupmyeondong/", views.get_eupmyeondong),
]