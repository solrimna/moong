from .models import Post
from .forms import PostForm
from django.contrib import messages
from locations.models import Location
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404


# !!!!!!!!로그인 필수 
def post_add(request):
    print("post_add 뷰 호출됨!")
    if request.method == 'POST':
        print("post_add POST 호출됨!")
        form = PostForm(request.POST)
    
        if form.is_valid():
            # #임시저장 버튼 선언 필요 
            # #is_temp = '임시저장' in request.POST
            # # 선택한 시/도, 시/군/구, 읍/면/동으로 Location 찾기
            # sido = form.cleaned_data['sido']
            # sigungu = form.cleaned_data['sigungu']
            # eupmyeondong = form.cleaned_data.get('eupmyeondong', '')
            # try:
            #     location = Location.objects.get(
            #         sido=sido,
            #         sigungu=sigungu,
            #         eupmyeondong=eupmyeondong
            #     )
            #     post.location = location
            # except Location.DoesNotExist:
            #     messages.error(request, '선택한 지역을 찾을 수 없습니다.')
            #     return render(request, 'moong/post_add.html', {'form': form})
            post = form.save(commit=False)
            post.author = request.user 

            if 'save_temp' in request.POST :
                post.complete = False
                post.save()
                messages.success(request, '임시저장')
                print("post_add 임시 저장 호출됨!")
            else : 
                post.complete = True
                post.save()
                messages.success(request, '게시글이 작성 완료되었습니다.')
                print("post_add 작성 완료 호출됨!")
            return redirect('moong:post_detail', post_id=post.id)
        else:
            messages.error(request, '입력 내용을 확인하세요.')
            print("post_add 입력값 확인으로 빠짐!")
    else:
        print("post_add else 호출됨!")
        form = PostForm()

    return render(request, 'moong/post_add.html', {'form' : form })

def post_list(request):
    """게시글 목록"""
    posts = Post.objects.filter(
        save=True,
        is_cancelled=False
    ).select_related('author', 'location').order_by('-create_time')
    
    return render(request, 'moong/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    """게시글 상세"""
    post = get_object_or_404(
        Post.select_related('author', 'location'),
        id=post_id
    )
    
    return render(request, 'moong/post_detail.html', {'post': post})