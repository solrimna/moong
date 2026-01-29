from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """커스텀 User 모델을 위한 Admin"""

    # 리스트 화면에서 보여줄 필드
    list_display = ['username', 'nick_name', 'ddomoong', 'date_joined']
    
    # 검색 가능한 필드
    search_fields = ['nick_name', 'email']
    
    # 필터
    list_filter = ['is_staff', 'is_superuser', 'date_joined']
    
    # 상세 화면 필드 그룹핑
    fieldsets = (
        ( None, {"fields" : ("username", "password","email", "phone")}),
        ( "활동 정보", {"fields" : ("nick_name", "location", "profile_image", "gender", "ddomoong")}),
        ( "권한", { "fields": ("is_active", "is_staff", "is_superuser")}),
        ( "중요한 일정", { "fields": ("last_login", "date_joined")}),
        
    )
