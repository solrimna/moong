from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.db.models import Count
from .models import Post, Hashtag, Image, Participation, Comment
from locations.models import Location
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
import openai
import os
from dotenv import load_dotenv

# OpenAI 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



# 메인 페이지
def main(request):
    # 검색하면 필터링해서 메인페이지에서 바로
    search = request.GET.get('search', '')
    
    posts = Post.objects.filter(
        complete=True,
        is_cancelled=False,
        moim_finished=False
    ).prefetch_related('images', 'hashtags')

    # 검색어가 있으면 추가 필터
    if search:
        posts = posts.filter(content__icontains=search)

    # 정렬
    posts = posts.order_by('-create_time')

    # 해시태그 리스트
    active_tags = Hashtag.objects.annotate(
        num_posts=Count('posts')
    ).filter(num_posts__gt=0).order_by('-num_posts')
    
    # Location 모델에서 모든 지역 키워드 수집
    location_keywords = set()
    loc_data = Location.objects.values_list('sido', 'sigungu', 'eupmyeondong')
    
    for loc in loc_data:
        for name in filter(None, loc):
            # 1. 원본 추가
            location_keywords.add(name)
            
            # 2. "서울특별시" → "서울"
            clean_name = name.replace('특별시', '').replace('광역시', '').replace('특별자치시', '').replace('특별자치도', '').replace('도', '')
            # "전라남도" -> "전남", "경상북도" -> "경북" 처럼 앞글자+세번째글자 조합
            if '남도' in name or '북도' in name:
                short_name = name[0] + name[2] # 예: '전' + '남'
                location_keywords.add(short_name)
            
            location_keywords.add(clean_name)
            
            # 3. "강남구" → "강남"
            if clean_name.endswith('구'):
                location_keywords.add(clean_name[:-1])
            elif clean_name.endswith('시'):
                location_keywords.add(clean_name[:-1])
            elif clean_name.endswith('군'):
                location_keywords.add(clean_name[:-1])
    
    # 지역 태그와 키워드 태그 구분...
    location_tags = []
    keyword_tags = []
    
    for tag in active_tags:
        # '부분 일치'를 빼고 '정확히 일치'하는지만. 운동 이런것도 '동'으로 인식함 ㅜㅜ
       
        if tag.name in location_keywords:
            location_tags.append(tag)
        else:
            keyword_tags.append(tag)

    # comment_form = CommentForm()        
    
    return render(request, 'moong/main.html', {
        'posts': posts,
        'location_tags': location_tags[:10],  # 상위 10개만
        'keyword_tags': keyword_tags[:10],    # 상위 10개만
        'search': search,
        # 'comment_form': comment_form,
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
다음 정보로 SNS 해시태그 6개를 만들어줘.
장소: {location}
내용: {content}

조건:
- # 기호 없이 단어나 명사만 출력
- 쉼표(,)로 구분하고 한글로만 작성
- 장소 해시태그 3개, 내용 해시태그 3개 만들기
- 지역 해시태그는 장소 정보에서 추출하고, 키워드 해시태그는 내용에서 추출
- 키워드 해시태그 예: 맛집, 취미, 친목, 운동 등
- 장소 해시태그 규칙(입력 데이터는 항상 A B C 3단계 형식):
    1. A (광역시/도): 약칭으로 (예: 서울, 세종, 경기, 전북 등)
    2. B (시/군/구): 마지막 글자 제외 (예: 순천, 강남, 의왕 등)
    3. C (읍/면/동): 전체 단어 그대로 (예: 정자동 등)

답변:"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        
        result = response.choices[0].message.content.strip()
        tags = [tag.strip().replace('#', '') for tag in result.split(',') if tag.strip()]
        
        return tags[:6]  # 최대 6개만
        
    except Exception as e:
        print(f"AI 해시태그 생성 오류: {e}")
        return []

# ==================== 게시글 작성 ====================
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
            location = get_fixed_location(location)

            location_text = ""
            if location:
                location_text = f"{location.sido} | {location.sigungu} | {location.eupmyeondong}"
            
            post.location = location
            
            temp_post_id = request.POST.get('temp_post_id')

            # 임시 저장!
            if 'save_temp' in request.POST :
                # post 신규생성 or 있던거 가져오기
                post, is_updated = get_or_create_post(
                    temp_post_id, 
                    request.user, 
                    form, 
                    location, 
                    complete=False
                )
                # is_updated ture면 -> 갱신 : 이미지 지웠다가 재저장 해줘야해서 clear true
                save_or_clear_images(post, request, clear_all=is_updated)

                # AI 해시태그
                tags = ai_tags(post.content, location_text)

                messages.success(request, '임시저장 완료!')
                print("post_add 임시 저장 호출됨!")
                print(f"임시 저장한 location: {post.location}")

                return render(request, 'moong/post_add.html', {
                    'form': form,
                    'tags': tags,
                    'temp_post': post,
                })
            # 최종 저장!
            else :    
                post, is_updated = get_or_create_post(
                    temp_post_id, 
                    request.user, 
                    form, 
                    location, 
                    complete=True
                )             
                save_or_clear_images(post, request, clear_all=True)

                # 해시태그 저장
                selected_tags = request.POST.getlist('tags')
                
                if selected_tags:
                    post.hashtags.clear()
                    for tag_name in selected_tags:
                        tag_name = tag_name.strip()
                        if tag_name:
                            tag_name = tag_name.replace("#", "")
                            tag, created = Hashtag.objects.get_or_create(name=tag_name)
                            post.hashtags.add(tag)
                else:
                    tags = ai_tags(post.content, location_text)
                    for tag_name in tags:
                        if tag_name.strip():
                            tag, created = Hashtag.objects.get_or_create(name=tag_name.strip())
                            post.hashtags.add(tag)
                
                messages.success(request, '게시 완료!')
                Participation.objects.get_or_create(
                    post=post,
                    user=request.user,
                    defaults={'status': 'APPROVED'}
                )
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
                    messages.error(request, f'- {error}')

            print("post_add 입력값 확인으로 빠짐!")

            context = {
                'form': form,
            }
            return render(request, 'moong/post_add.html', context)
    else: # GET 
        #load_temp  = YES -> 임시 저장글 가져오기
        #           = NO  -> 새글 작성
        #           = NONE -> 임시 저장 글이 있는지 확인 -> post_add_confirm reqeust 
        #                   -> 결정에 따라서 실제 게시글 작성 동작
        load_temp = request.GET.get('load_temp')

        if load_temp == 'yes':
            # 임시저장 글 불러오기
            temp_post = Post.objects.filter(
                author=request.user,
                complete=False
            ).order_by('-create_time').first()
            
            if temp_post:
                form = PostForm(instance=temp_post)
                existing_images = temp_post.images.all().order_by('order')
                existing_tags = [f"#{tag.name}" for tag in temp_post.hashtags.all()]
                
                messages.success(request, '임시저장된 글을 불러왔습니다.')

                print(f"임시저장 - 불러온 location: {temp_post.location}")

                context = {
                    'form': form,
                    'temp_post': temp_post,
                    'existing_images': existing_images,
                    'tags': existing_tags,
                }
                return render(request, 'moong/post_add.html', context)
            else:
                messages.warning(request, '불러올 임시저장 글이 없습니다.')
                form = PostForm()
        
        elif load_temp == 'no':
            # 새 글 작성
            form = PostForm()
        
        else:
            # 임시저장 글이 있는지 확인
            print(f"임시저장 글이 있는지 확인")  
            temp_post = Post.objects.filter(
                author=request.user,
                complete=False
            ).order_by('-create_time').first()
            
            if temp_post:
                print(f"임시저장 사용여부 호출")  
                return redirect('moong:post_add_confirm')
            else:
                # 임시저장 글이 없으면 바로 작성 화면
                form = PostForm()

    return render(request, 'moong/post_add.html', {'form': form})

# ==================== 단순 임시 저장 여부 확인 ====================
@login_required
def post_add_confirm(request):
    temp_post = Post.objects.filter(
        author=request.user,
        complete=False
    ).order_by('-create_time').first()
    
    if temp_post:
        context = {
            'has_temp_post': True,
            'temp_post': temp_post,
        }
        return render(request, 'moong/post_add_confirm.html', context)
    else:
        # 임시저장 글이 없으면 바로 작성 페이지로
        return redirect('moong:post_add')

# ==================== 게시글 상세 ====================
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'location'),
        id=post_id
    )
    approved_participants = post.participations.filter(status='APPROVED').select_related('user')
    is_applied = False #is_applied 초기화
    if request.user.is_authenticated:
        is_applied = post.participations.filter(user=request.user).exists()

    comments = post.comments.select_related('author').order_by('create_time')
    images = post.images.all()
    hashtags = post.hashtags.all()

    comment_form = CommentForm()

    return render(request, 'moong/post_detail.html', {'post': post,
                                                      'comments':comments,
                                                      'comment_form':comment_form,
                                                      'is_applied': is_applied,
                                                      'approved_participants': approved_participants,
                                                      })

# ==================== 게시글 수정 ====================
def post_mod(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    print("post_mod 뷰 호출됨!")
    # 권한 체크: 작성자만 수정 가능
    if post.author != request.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('moong:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        print("post_mod 호출됨!")
        form = PostForm(data=request.POST, files=request.FILES, instance=post)
    
        if form.is_valid():
            post = form.save(commit=False)

            location = form.cleaned_data.get("location")
            location = get_fixed_location(location)
            post.location = location

            post.complete = True
            post.save()

            save_or_clear_images(post, request, clear_list='delete_images')
            
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
            
            messages.success(request, '게시글이 수정되었습니다.')
            print("post_mod 수정 완료 호출됨!")

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

            print("post_mod 입력값 확인으로 빠짐!")
    else:
        print("post_mod GET 호출됨!")
        form = PostForm(instance=post)

    # 기존 이미지 목록
    existing_images = post.images.all()

    context = {
        'form': form,
        'post': post,
        'existing_images': existing_images,
    }

    return render(request, 'moong/post_mod.html', context)

# ==================== 게시글 삭제 ====================
@login_required
def post_delete(request, post_id):
    print("post_delete 게시글 삭제 호출됨!")
    post = get_object_or_404(Post, id=post_id)
    
    # 권한 체크
    if post.author != request.user:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('moong:post_detail', post_id=post_id)
    
    # POST 요청만 허용
    if request.method == 'POST':
        approved_count = post.get_approved_count()

        # case1. 승인된 참여자가 없는 case
        if approved_count == 0:
            # 이미지 파일 삭제
            for image in post.images.all():
                if image.image:
                    image.image.delete()
            
            post.delete()
        # case2. 승인된 참여자가 있는 case
        else:
            print(f"게시글 폭파 처리 - (확정 참여자: {approved_count}명)으로 인해 진행")
            post.is_cancelled = True
            post.save()
            messages.warning(request, f'확정 참여자({approved_count}명)가 있어 모임글이 비활성화 되었습니다.')
            print("post_delete 폭파 처리 완료!")

        messages.success(request, '게시글이 삭제되었습니다.')
        return redirect('moong:main')
    else:
        # GET 요청은 거부
        return redirect('moong:post_detail', post_id=post_id)
       
# ==================== 모집 확정 ====================
@login_required
def post_closed(request, post_id):
    print("post_closed 모집 확정 호출됨!")
    post = get_object_or_404(Post, id=post_id)
    
    # 권한 체크
    if post.author != request.user:
        messages.error(request, '모집 확정 권한이 없습니다.')
        return redirect('moong:post_detail', post_id=post_id)
    
    # POST 요청만 허용
    if request.method == 'POST':
        approved_count = post.get_approved_count()

        # # case1. 승인된 참여자가 없는 case
        if approved_count == 0:
            print(f"게시글 모집 확정 불가 - 확정 참여자 없음")
            messages.warning(request, f'모임 참여자가 없어 모집 확정이 불가능합니다.')
        # case2. 승인된 참여자가 있는 case
        else:
            print(f"게시글 모집 확정 처리 - (확정 참여자: {approved_count}명)으로 진행")
            post.is_closed = True
            post.save()
            messages.warning(request, f'확정 참여자({approved_count}명) 상태로 모임이 확정되었습니다.')
            print("게시글 모집 확정 완료!")

        # 모임이 확정되던 아니던 post_detail로 
        return redirect('moong:post_detail', post_id=post_id)
    else:
        # GET 요청은 거부
        return redirect('moong:post_detail', post_id=post_id)

# ==================== 모임 완료(확정 뒤에) ====================
@login_required
def moim_finished(request, post_id):
    print("moim_finished 호출됨!")
    post = get_object_or_404(Post, id=post_id)
    
    # 권한 체크
    if post.author != request.user:
        messages.error(request, '권한이 없습니다.')
        return redirect('moong:post_detail', post_id=post_id)
    
    # 모집 확정되지 않은 모임은 완료 불가
    if not post.is_closed:
        messages.error(request, '모집이 확정되지 않은 모임입니다.')
        return redirect('moong:post_detail', post_id=post_id)
    
    # POST 요청만 허용
    if request.method == 'POST':
        post.moim_finished = True  # 모임 완료 필드 (추가 필요)
        post.save()
        
        messages.success(request, '모임이 완료 처리되었습니다.')
        print("모임 완료 처리 완료!")
        return redirect('moong:main')
    
    return redirect('moong:post_detail', post_id=post_id)    

#참여 신청, 참여 취소
@login_required
def post_apply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # 이미 신청했는지 확인 후 없으면 생성
    participation, created =Participation.objects.get_or_create(post=post, user=request.user, defaults={'status': 'APPROVED'})
    messages.success(request, '참여 신청이 완료되었습니다.')
    return redirect('moong:post_detail', post_id=post.id) # 다시 상세페이지로!

@login_required
def post_cancel(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # 해당 신청 내역 찾아서 삭제
    participation = Participation.objects.filter(post=post, user=request.user)
    if participation.exists():
        participation.delete()
        messages.success(request, '참여 신청이 취소되었습니다.')
    return redirect('moong:post_detail', post_id=post.id) # 다시 상세페이지로!

# ==================== 댓글 추가 ====================
@login_required
def comment_add(request, post_id):
    if request.method != "POST":
        return HttpResponseBadRequest()
    
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        # url_next = reverse("moong:post_detail",
        #                    kwargs={"post_id":comment.post_id}
        #                    ) + f"#post-{comment.post.id}"
        # return HttpResponseRedirect(url_next)
    else:
        return HttpResponseBadRequest("댓글 내용 오류")
    
    return redirect("moong:post_detail", post_id=post.id)


# ==================== 댓글 삭제 ====================    
@login_required
def comment_delete(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(Comment, id=comment_id)

        if comment.author == request.user:
            comment.delete()
            url_next = reverse("moong:post_detail",
                               kwargs={"post_id":comment.post_id}
                               ) + f"#post-{comment.post.id}"
            return HttpResponseRedirect(url_next)
        else:
            return HttpResponseForbidden("작성자만 댓글을 삭제할 수 있습니다.")
    else:
        return HttpResponseBadRequest()
    
# @login_required
# def comment_delete(request, comment_id):
#     if request.method != "POST":
#         return HttpResponseBadRequest()

#     comment = get_object_or_404(Comment, id=comment_id)

#     if comment.author != request.user:
#         return HttpResponseForbidden("작성자만 댓글을 삭제할 수 있습니다.")

#     post_id = comment.post.id
#     comment.delete()
#     return redirect("moong:post_detail", post_id=post_id)    








# ===============================================================================================================================================================================
# ==================== 공통 사용용 def ============================================================================================================================================
# 읍/면/동 위치보정 함수 별도 분기
def get_fixed_location(location):
    if not location:
        return None
    print(f"get_fixed_location - sido: {location.sido}")  
    print(f"get_fixed_location - sigungu: {location.sigungu}")  
    print(f"get_fixed_location - eupmyeondong: {location.eupmyeondong}")
    
    if location and not location.eupmyeondong:
        print(f"주소 보정 함수 호출")
        fixed_location = Location.objects.filter(
            sido=location.sido,
            sigungu=location.sigungu,
            eupmyeondong=location.sigungu
        ).first()
        return fixed_location if fixed_location else location
    
    return location    

# ==================== POST 신규 생성 or 기존거 가져오기====================   
# return 값 - post, is_updated
def get_or_create_post(temp_post_id, author, form, location, complete=False):
    print(f"넘어온 데이터 확인 : temp_post_id: {temp_post_id}")
    if temp_post_id:
        try:
            post = Post.objects.get(id=temp_post_id, author=author, complete=False)
            print(f"기존 post 찾음! ID: {post.id}")
            post.content = form.cleaned_data.get('content')
            post.title = form.cleaned_data.get('title')
            post.moim_date = form.cleaned_data.get('moim_date')
            post.moim_time = form.cleaned_data.get('moim_time')
            post.max_people = form.cleaned_data.get('max_people')
            post.location = location
            post.complete = complete
            post.save()
            return post, True  # 갱신일 때 
        except Post.DoesNotExist:
            pass
    
    # 새로 생성
    post = form.save(commit=False)
    post.author = author
    post.location = location
    post.complete = complete
    post.save()
    return post, False

# ==================== 이미지 삭제 or 저장(flag따름) =======
# clear_all     : 전체 삭제
# clear_list    : 선택 삭제 
def save_or_clear_images(post, request, clear_all=False, clear_list=None):
    
    if clear_list:
        delete_images = request.POST.getlist(clear_list)
        if delete_images:
            Image.objects.filter(id__in=delete_images).delete()
            print(f"선택 삭제된 이미지: {len(delete_images)}개")

    if clear_all:
        post.images.all().delete()

    images = request.FILES.getlist('images')
    if not images:
        return  
    
    # 이미지 다 지우는거 아닌거 고려 
    last_image = post.images.order_by('-order').first()
    start_order = (last_image.order + 1) if last_image else 0
    
    for idx, img_file in enumerate(images):
        Image.objects.create(
            post=post, 
            image=img_file, 
            order=start_order + idx 
        )
    print(f"추가된 이미지: {len(images)}개")
