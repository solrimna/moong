from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Post, Hashtag, Image
from locations.models import Location
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from django.contrib import messages
from django.http import JsonResponse
import openai
import os
from dotenv import load_dotenv

# OpenAI 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



# 메인 페이지
def main(request):
    # 검색하면 필터링해서 메인페이지에서 바로 보여줌
    search = request.GET.get('search', '')
    
    if search:
        posts = Post.objects.filter(
            complete=True,
            content__icontains=search
        ).prefetch_related('images', 'hashtags').order_by('-create_time')
    else:
        posts = Post.objects.filter(
            complete=True
        ).prefetch_related('images', 'hashtags').order_by('-create_time')
    
    # 해시태그 리스트
    active_tags = Hashtag.objects.annotate(
        num_posts=Count('posts')
    ).filter(num_posts__gt=0).order_by('-num_posts')
    
    # Location 모델에서 모든 지역 명칭 가져오기
    loc_data = Location.objects.values_list('sido', 'sigungu', 'eupmyeondong')
    location_names = set()
    for loc in loc_data:
        location_names.update(filter(None, loc))  # None 제외하고 추가
    
    # 지역 태그와 키워드 태그 구분
    location_tags = []
    keyword_tags = []
    
    for tag in active_tags:
        if tag.name in location_names:
            location_tags.append(tag)
        else:
            keyword_tags.append(tag)
    
    return render(request, 'moong/main.html', {
        'posts': posts,
        'location_tags': location_tags[:10],  # 상위 10개만
        'keyword_tags': keyword_tags[:10],    # 상위 10개만
        'search': search,
    })



# 해시태그별 게시물 보기
def tag_feeds(request, tag_name):
    posts = Post.objects.filter(
        hashtags__name=tag_name,
        complete=True
    ).prefetch_related('images', 'hashtags').order_by('-create_time')
    
    return render(request, 'moong/tag_feeds.html', {
        'tag_name': tag_name,
        'posts': posts,
    })




# ai 해시태그 쓰려면 pip install openai, pip install python-dotenv 해야합니다!
# .env 파일 manage.py 파일과 같은 곳에 놓고, .env 안에 open ai key 넣으셔야 합니다.
# .gitignore에도 .env 넣어주세욥~
# AI 해시태그 생성 함수
def ai_tags(content, location):
    """내용과 장소를 바탕으로 해시태그 5개 생성"""
    
    if not content and not location:
        return []
    
    prompt = f"""
다음 정보로 SNS 해시태그 5개를 만들어줘.
장소: {location}
내용: {content}

조건:
- # 기호 없이 단어, 명사만 출력
- 쉼표로 구분
- 한글로 작성
- 예시: 강남, 맛집, 데이트, 카페, 주말

답변:"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        
        result = response.choices[0].message.content.strip()
        tags = [tag.strip().replace('#', '') for tag in result.split(',') if tag.strip()]
        
        return tags[:5]  # 최대 5개만
        
    except Exception as e:
        print(f"AI 해시태그 생성 오류: {e}")
        return []


@login_required
def post_add(request):
    print("post_add 뷰 호출됨!")
    if request.method == 'POST':
        print("post_add POST 호출됨!")
        form = PostForm(data=request.POST, files=request.FILES)
    
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user 

            location = form.cleaned_data.get("location")
            
            if location:
                print(f"sido: {location.sido}")  # 가능!
                print(f"sigungu: {location.sigungu}")  # 가능!
                print(f"eupmyeondong: {location.eupmyeondong}")  # 가능!
                
            # ✅ 2단계까지만 있는 지역 자동 보정 (세종 새롬동 케이스)
            if location and not location.eupmyeondong:
                fixed_location = Location.objects.filter(
                    sido=location.sido,
                    sigungu=location.sigungu,
                    eupmyeondong=location.sigungu
                ).first()

                if fixed_location:
                    location = fixed_location

            post.location = location

            if 'save_temp' in request.POST :
                post.complete = False
                post.save()
                messages.success(request, '임시저장')
                print("post_add 임시 저장 호출됨!")
            else : 
                post.complete = True
                post.save()

                images = request.FILES.getlist('images')
                for idx, image_file in enumerate(images):
                    Image.objects.create(
                        post=post,
                        image=image_file,
                        order=idx
                    )
                try:
                    # AI로 해시태그 자동 생성
                    tags = ai_tags(post.content, '')   # 두번째인자 공백 아니고 원래 location

                    # 해시태그 저장
                    for tag_name in tags:
                        if tag_name.strip():
                            tag, created = Hashtag.objects.get_or_create(name=tag_name.strip())
                            post.hashtags.add(tag)
                        
                except Exception as e:
                    print(f"해시태그 생성 실패: {e}")
                
                messages.success(request, '게시글이 작성 완료되었습니다.')
                print("post_add 작성 완료 호출됨!")

                return redirect('moong:post_detail', post_id=post.id)
            
        else:
            print("="*50)
            print("폼 유효성 검사 실패!")
            print("에러:", form.errors)
            print("에러 (JSON):", form.errors.as_json())
            print("="*50)

            messages.error(request, '입력 내용을 확인하세요.')
            # 각 필드별 에러도 메시지로 추가
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

            print("post_add 입력값 확인으로 빠짐!")
    else:
        print("post_add else 호출됨!")
        form = PostForm()

    return render(request, 'moong/post_add.html', {'form' : form })

def post_detail(request, post_id):
    """게시글 상세"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'location'),
        id=post_id
    )
    
    comments = post.comments.select_related('author').order_by('create_time')
    images = post.images.all()
    hashtags = post.hashtags.all()

    return render(request, 'moong/post_detail.html', {'post': post})