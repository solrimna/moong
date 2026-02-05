from django.conf import settings

# Context processor - 모든 템플릿에 자동으로 변수를 넣어주는 함수
# settings.py의 context_processors 목록에 등록하여 활성화
def kakao_app_key(request):
    return {"KAKAO_APP_KEY": settings.KAKAO_APP_KEY}
