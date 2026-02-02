from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.db.models import Count
from .models import Post, Hashtag, Image, Participation, Comment, Ddomoong
from locations.models import Location
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
import openai
import os
from dotenv import load_dotenv
from django.utils import timezone
# OpenAI 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# ============ 메인 페이지 =============
# 첫번째: location 모델에서 지역 키워드 추출하는 함수
def get_location_keywords():
    location_keywords = set()
    loc_data = Location.objects.values_list('sido', 'sigungu', 'eupmyeondong')
    
    for loc in loc_data:
        for name in filter(None, loc):
          
            location_keywords.add(name)
            
            # 서울특별시 → 서울
            clean_name = name.replace('특별시', '').replace('광역시', '').replace('특별자치시', '').replace('특별자치도', '').replace('도', '')
            
            # 전라남도 → 전남
            if '남도' in name or '북도' in name:
                location_keywords.add(name[0] + name[2])
            
            location_keywords.add(clean_name)

    return location_keywords


# 두번째: 해시태그 지역/키워드로 분류하는 함수
def categorize_hashtags(active_tags, location_keywords):
    location_tags = []
    keyword_tags = []
    
    for tag in active_tags:
        if tag.name in location_keywords:
            location_tags.append(tag)
        else:
            keyword_tags.append(tag)
    
    return location_tags[:10], keyword_tags[:10]


# url 연결된 찐 main 함수
def main(request):
    search = request.GET.get('search', '')
    
    posts = Post.objects.filter(
        complete=True,
        is_cancelled=False,
        moim_finished=False
    ).prefetch_related('images', 'hashtags')

    if search:
        posts = posts.filter(content__icontains=search)

    posts = posts.order_by('-create_time')

    active_tags = Hashtag.objects.annotate(
        num_posts=Count('posts')
    ).filter(num_posts__gt=0).order_by('-num_posts')
    
    # 함수로 분리된거 불러오기~
    location_keywords = get_location_keywords()
    location_tags, keyword_tags = categorize_hashtags(active_tags, location_keywords)
    
    comment_form = CommentForm()        

    return render(request, 'moong/main.html', {
        'posts': posts,
        'location_tags': location_tags,
        'keyword_tags': keyword_tags,
        'search': search,
        # 'comment_form': comment_form,  # 메인 페이지 댓글 작성폼 노출 여부
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
# ================ 해시태그 생성 함수 ======================
# 지역 해시태그를 파싱으로 바꿔서 지역 해시태그, 키워드 해시태그 함수 나눴습니다!
def extract_location_tags(location):
    if not location or not isinstance(location, str):
        return []

    loc_tags = []
    if location and isinstance(location, str):
        # 오류 날때 ' | ' 이런 이상한 해시태그가 생겨서 없앴어요
        clean_location = location.replace('|', ' ').strip()
        parts = [p.strip() for p in clean_location.split() if p.strip()]
        
        if len(parts) > 0:
            # 광역시/도 (이 부분이 문제가 많아서 아예 다 써놨어요)
            a = parts[0]
            short_names = {
                "강원특별자치도": "강원", "경기도": "경기",
                "경상남도": "경남", "경상북도": "경북", "광주광역시": "광주",
                "대구광역시": "대구", "대전광역시": "대전", "부산광역시": "부산",
                "서울특별시": "서울", "세종특별자치시": "세종", "울산광역시": "울산",
                "인천광역시": "인천", "전라남도": "전남",
                "전북특별자치도": "전북", "제주특별자치도": "제주",
                "충청남도": "충남", "충청북도": "충북"
            }
            a_short = short_names.get(a, a[:2])
            loc_tags.append(a_short)

            # 나머지 주소
            details = []
            for p in parts[1:]:
                p_clean = p.strip()
                # ' | ' 문자나 이름 겹치지 않는 것만 추가
                if p_clean and p_clean not in ['|', 'None', 'null'] and p_clean not in details:
                    details.append(p_clean)
    
            loc_tags.extend(details[:2])
    return loc_tags

# ai로 키워드 해시태그만 추출하기
def ai_tags(content, location):
    if not content and not location:
        return []

    loc_tags = extract_location_tags(location)

    needed_count = 6 - len(loc_tags)
    prompt = f"""
내용: {content}
위 내용을 바탕으로 SNS 키워드 해시태그를 {needed_count}개 만들어줘.

조건:
- # 기호 없이 단어나 명사만 출력
- 쉼표(,)로 구분하고 한글로만 작성
- 글 내용 기반으로 키워드 해시태그 생성
- 예: 맛집, 취미, 카페, 운동 등

답변:"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "해시태그 생성기"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        ) # 키워드 해시태그가 너무 엉뚱하게 나오면 temperature를 0에 가깝게 줄이고,
          # 좀 더 창의적으로 나오길 원하시면 0.5 정도로 늘리면 돼요.
        
        result = response.choices[0].message.content.strip()
        keyword_tags = [k.strip().replace('#', '') for k in result.split(',') if k.strip()]
        
        # 합치기~
        total_tags = [t for t in (loc_tags + keyword_tags) if t and t != '|']
        return total_tags[:6]
        
    except Exception:
        return [t for t in loc_tags if t != '|']


# ==================== 게시글 작성 + 수정 ===================
@login_required
def post_form(request, post_id=None):

    is_edit = post_id is not None
    post = None
    
    # 수정 모드: 권한 체크
    if is_edit:
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            messages.error(request, '수정 권한이 없습니다.')
            return redirect('moong:post_detail', post_id=post_id)
        
    print("post_add 뷰 호출됨!")
    if request.method == 'POST':
        print("post_add POST 호출됨!")
        if is_edit:
            form = PostForm(data=request.POST, files=request.FILES, instance=post)
        else:
            form = PostForm(data=request.POST, files=request.FILES)
    
        if form.is_valid():
            location = form.cleaned_data.get("location")
            location = get_fixed_location(location)

            location_text = ""
            if location:
                location_text = f"{location.sido} | {location.sigungu} | {location.eupmyeondong}"
                        
            temp_post_id = request.POST.get('temp_post_id')

            # 임시 저장!
            if not is_edit and 'save_temp' in request.POST :
                # post 신규생성 or 있던거 가져오기
                post, is_updated = get_or_create_post(
                    temp_post_id, 
                    request.user, 
                    form, 
                    location, 
                    complete=False
                )
                # is_updated ture면 -> 갱신 : 이미지 지웠다가 재저장 해줘야해서 clear true
                save_or_clear_images(post, request, clear_all=False, clear_list='delete_images')

                # 1. AI 해시태그
                tags = ai_tags(post.content, location_text)

                # 2. 생성된 태그를 DB에 저장하고 post와 연결
                post.hashtags.clear()
                if tags:
                    for tag_name in tags:
                        tag_name = tag_name.strip().replace("#", "")
                        if tag_name:
                            tag, created = Hashtag.objects.get_or_create(name=tag_name)
                            post.hashtags.add(tag)

                messages.success(request, '임시저장 완료!')
                print("post_add 임시 저장 호출됨!")
                print(f"임시 저장한 location: {post.location}")

                url = reverse('moong:post_add') + '?load_temp=yes'
                return redirect(url)
            # 최종 저장!
            else :    
                if is_edit:
                    post = form.save(commit=False)
                    post.location = location
                    post.complete = True
                    post.save()
                    save_or_clear_images(post, request, clear_list='delete_images')
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
                
                
                if not is_edit:
                    Participation.objects.get_or_create(
                        post=post,
                        user=request.user,
                        defaults={'status': 'APPROVED'}
                    )
                    messages.success(request, '게시 완료!')
                else:
                    messages.success(request, '게시글이 수정되었습니다!')
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
                'is_edit': is_edit,
                'post': post,
            }
            if is_edit and post:
                context['existing_images'] = post.images.all()
            return render(request, 'moong/post_add.html', context)
    else: # GET 
        # 수정하기랑 합침 
        if is_edit:
            form = PostForm(instance=post)
            existing_images = post.images.all()
            existing_tags = [tag.name for tag in post.hashtags.all()]
            context = {
                'form': form,
                'is_edit': True,
                'post': post,
                'existing_images': existing_images,
                'tags': existing_tags,
            }
            return render(request, 'moong/post_add.html', context)
        
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
                existing_tags = [tag.name for tag in temp_post.hashtags.all()] # 이름만 리스트로 넘겨주기
                
                messages.success(request, '임시저장된 글을 불러왔습니다.')

                print(f"임시저장 - 불러온 location: {temp_post.location}")
                print(f"임시저장 - 불러온 images: {temp_post.images.all()}")
                context = {
                    'form': form,
                    'temp_post': temp_post,
                    'tags': existing_tags,
                    'existing_images': existing_images,
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
    approved_participants = post.participations.select_related('user')
    
    user_participation = None
    if request.user.is_authenticated:
        user_participation = Participation.objects.filter(
            post=post,
            user=request.user
        ).first()

    comments = (
        post.comments
        .filter(parent__isnull=True)
        .select_related('author')
        .prefetch_related('replies__author')
        .order_by('create_time'))
    
    images = post.images.all()
    hashtags = post.hashtags.all()

    comment_form = CommentForm()
    # 참여자 리스트 (승인 & 승인 리스트 & 대기 list)
    approval_list = []
    index_participant_list = []
    index_indicator = False
    index_participant = 0
    print(user_participation)
    for user in list(approved_participants):
        for index, item in enumerate(list(approved_participants)):
            if item == user and ((index + 1) > post.max_people):
                index_participant = (index + 1) - post.max_people
                index_indicator = True
        index_participant_list.append(index_participant)
        approval_list.append(index_indicator)
    
    # 또뭉 참여자 리스트 (모임 완료 + COMPLETED + 본인 제외)
    ddomoong_participants = []
    if post.moim_finished and request.user.is_authenticated:
        ddomoong_participants = list(
            post.participations.filter(
                status='COMPLETED'
            ).select_related('user').exclude(
                user=request.user
            )
        )
        for p in ddomoong_participants:
            p.is_ddo_by_me = p.ddomoongs.filter(from_user=request.user).exists()

    context = {
        'post': post,
        'comments':comments,
        'comment_form':comment_form,
        'approved_participants_and_approval': zip(approved_participants,approval_list, index_participant_list),
        'user_participation': user_participation,
        'index_participant': index_participant,
                'ddomoong_participants': ddomoong_participants,
    }
    
    
    return render(request, 'moong/post_detail.html', context)

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

# ==================== 모집 확정 / 확정 취소 ====================
@login_required
def post_closed_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 권한 체크
    if post.author != request.user:
        messages.error(request, '권한이 없습니다.', extra_tags='alert_popup')
        return redirect('moong:post_detail', post_id=post_id)

    # POST 요청만 허용
    if request.method == 'POST':
        if post.is_closed:
            # 확정 취소
            post.is_closed = False
            post.save()
            messages.warning(request, '모집 확정이 취소되었습니다.', extra_tags='alert_popup')
            print("게시글 모집 확정 취소 완료!")
        else:
            # 확정
            approved_count = post.get_approved_count()
            if approved_count == 0:
                messages.warning(request, '모임 참여자가 없어 모집 확정이 불가능합니다.', extra_tags='alert_popup')
            else:
                post.is_closed = True
                post.save()
                messages.warning(request, f'확정 참여자({approved_count}명) 상태로 모임이 확정되었습니다.', extra_tags='alert_popup')
                print("게시글 모집 확정 완료!")

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
        post.moim_finished = True
        post.save()

        # 참여자들 상태도 바꿔줘야함  APPROVED > COMPLETED
        post.participations.filter(status='APPROVED').update(status='COMPLETED')

        messages.success(request, '모임이 완료 처리되었습니다.')
        print("모임 완료 처리 완료!")
        return redirect('moong:main')
    
    return redirect('moong:post_detail', post_id=post_id)    

#참여 신청, 참여 취소
@login_required
def participation_apply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # 이미 신청했는지 확인 후 없으면 생성    
    
    participation, created =Participation.objects.get_or_create(
        post=post, 
        user=request.user, 
        defaults={'status': 'PENDING',
                  'approve_time' : timezone.now()
                  }, 
        )
    print(f"참여 확인 :  {participation}, created : {created}")
    messages.success(request, '참여 신청이 완료되었습니다.')
    return redirect('moong:post_detail', post_id = post.id) # 다시 상세페이지로!

@login_required
def participation_manage(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    #print(f"승인여부 :  {action_comple}")
    # 주최자만 권한 허용
    if request.user != participation.post.author:
        return redirect('moong:post_detail', post_id=participation.post.id)

    if request.method == 'POST':
        action_complete = request.POST.get('action_complete')
        print(f"승인여부 :  {action_complete}")
        if action_complete == 'approve':
            participation.status = 'APPROVED' # 수락 시 승인 상태로 변경
            participation.save()
        elif action_complete == 'reject':
            # 거절 시 다시 신청할 수 있도록 아예 삭제하거나 상태를 REJECTED로 변경
            participation.cancel() 
            
    return redirect('moong:post_detail', post_id=participation.post.id)    


@login_required
def participation_cancel(request, post_id):
    print("참여 취소 호출")
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
    parent_id = request.POST.get("parent_id")

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        if parent_id:
            comment.parent = Comment.objects.get(id=parent_id)
        comment.save()    

        url_next = reverse("moong:post_detail",
                           kwargs={"post_id":comment.post_id}
                           ) + f"#post-{comment.post.id}"
        return HttpResponseRedirect(url_next)
    else:
        return HttpResponseBadRequest("댓글 내용 오류")
    
    # return redirect("moong:post_detail", post_id=post.id)


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


# ==================== 또뭉 주기 ====================   
@login_required
def give_ddomoong(request, participation_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 가능'}, status=400)
    participation = get_object_or_404(Participation, id=participation_id)
    
    # 자기 자신에게는 못 줌
    if participation.user == request.user:
        return JsonResponse({
            'success': False,
            'message': '자기 자신에게는 또뭉을 줄 수 없어요!'
        })
    
    # 별도 table에 저장
    ddomoong = Ddomoong.objects.filter(
        participation=participation,
        from_user=request.user
    )
    
    if ddomoong.exists():
        ddomoong.delete()
        participation.user.decrease_ddomoong()
        is_ddo = False
        message = '또뭉을 취소했어요!'
    else:
        Ddomoong.objects.create(
            participation=participation,
            from_user=request.user
        )
        participation.user.increase_ddomoong()
        is_ddo = True
        message = '또뭉을 줬어요! 👍'
    
    # 현재 또뭉 개수 
    participation.user.refresh_from_db(fields=['ddomoong'])
    ddo_count = participation.user.ddomoong
    print(f'또뭉 카운트 : {ddo_count}')
    return JsonResponse({
        'success': True,
        'is_ddo': is_ddo,
        'ddo_count': ddo_count,
        'message': message
    })

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
        print(f"clear_all true 확인 로그")
        post.images.all().delete()

    images = request.FILES.getlist('images')
    if not images:
        print(f"왜 임시저장 때 이미지가 없지?")
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
