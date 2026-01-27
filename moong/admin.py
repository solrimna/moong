from django.contrib import admin
from .models import Post, Hashtag, Image


# 테스트용으로 대충
admin.site.register(Post)
admin.site.register(Hashtag)
admin.site.register(Image)