from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm, LoginForm, ProfileEditForm
from .models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from locations.models import Location
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from moong.models import Post, Participation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            location = form.cleaned_data.get("location")

            # ✅ 2단계까지만 있는 지역 자동 보정 (세종 새롬동 케이스)
            if location and not location.eupmyeondong:
                fixed_location = Location.objects.filter(
                    sido=location.sido,
                    sigungu=location.sigungu,
                    eupmyeondong=location.sigungu
                ).first()

                if fixed_location:
                    location = fixed_location

            user.location = location
            user.save()

            print("✅ USER SAVED:", user)
            return redirect("users:login")
        else:
            print("❌ FORM ERRORS:", form.errors)

    else:
        form = SignupForm()
       
    context = {"form": form}

    return render(request, "users/signup.html", context)


# 마이페이지 조회
@login_required
def mypage(request):
    """마이페이지 - 프로필 조회"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'users/mypage.html', context)


# 프로필 수정
@login_required
def mypage_edit(request):
    """마이페이지 - 프로필 수정"""
    user = request.user
    
    if request.method == 'POST':
        # 🔥 기본 프로필로 변경 버튼을 눌렀을 때
        if 'reset_profile_image' in request.POST:
            user.profile_image = 'profile_images/custom_property.png'
            # update_fields를 사용해서 save() 메서드의 이미지 처리 건너뛰기
            User.objects.filter(pk=user.pk).update(profile_image='profile_images/custom_property.png')
            messages.success(request, '프로필 이미지가 기본 이미지로 변경되었습니다.')
            return redirect('users:mypage_edit')
        
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # 지역 정보는 따로 처리 (3단계 선택에서 전송됨)
            location_id = request.POST.get('location')
            if location_id:
                try:
                    user.location = Location.objects.get(id=location_id)
                except Location.DoesNotExist:
                    messages.error(request, '유효하지 않은 지역입니다.')
                    return redirect('users:mypage_edit')
            
            form.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('users:mypage')
        else:
            messages.error(request, '입력 내용을 확인해주세요.')
    else:
        form = ProfileEditForm(instance=user)
    
    context = {
        'user': user,
        'form': form,
    }
    
    return render(request, 'users/mypage_edit.html', context)


# 활동 이력 (메인)
@login_required
def mypage_activity(request):
    """마이페이지 - 활동 이력 메인"""
    user = request.user
    
    # 내가 만든 모임 (임시저장 제외, 완성된 글만)
    my_posts = Post.objects.filter(
        author=user,
        complete=True
    ).order_by('-create_time')
    
    # 내가 참여한 모임 
    my_participations = Participation.objects.filter(
        user=user,
        post__complete=True 
    ).select_related('post').order_by('-create_time')
    
    # 통계
    total_created = my_posts.count()
    total_participated = my_participations.count()

    context = {
        'user': user,
        'total_created': total_created,
        'total_participated': total_participated,
    }
    
    return render(request, 'users/mypage_activity.html', context)


# 개최한 모임 리스트 (페이지네이션)
@login_required
def mypage_created_list(request):
    """내가 개최한 모임 리스트 (페이지네이션)"""
    
    # 내가 만든 모임 가져오기
    my_posts = Post.objects.filter(
        author=request.user,
        complete=True  # 완성된 글만 (임시저장 제외)
    ).order_by('-create_time')  # ✅ create_time으로 수정!
    
    # 페이지네이션 (5개씩)
    paginator = Paginator(my_posts, 5)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # 나 외의 참여자 리스트 정리 (ddo_moong 포함, 모임 완료된 것만)
    for post in page_obj:
        if post.moim_finished:
            other_participants = list(
                post.participations.filter(
                    status='COMPLETED'
                ).select_related('user').exclude(
                    user=request.user
                )
            )
            for p in other_participants:
                p.is_ddo_by_me = p.ddomoongs.filter(from_user=request.user).exists()
            post.other_participants = other_participants
        else:
            post.other_participants = []
    
    context = {
        'page_obj': page_obj,
        'total_count': my_posts.count(),
    }
    
    return render(request, 'users/mypage_created_list.html', context)


# 참여한 모임 리스트 (페이지네이션)
@login_required
def mypage_participated_list(request):
    """내가 참여한 모임 리스트 (페이지네이션)"""
    
    # 내가 참여 신청한 모임 가져오기
    my_participations = Participation.objects.filter(
        user=request.user
    ).select_related('post', 'post__author').order_by('-create_time')  # ✅ create_time으로 수정!
    
    # 페이지네이션 (5개씩)
    paginator = Paginator(my_participations, 5)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # 나 외의 참여자 리스트 정리
    for participation in page_obj:
        if participation.post.moim_finished:
            other_participants = list(
                participation.post.participations.filter(
                    status='COMPLETED'
                ).select_related('user').exclude(
                    user=request.user
                )
            )
            for p in other_participants:
                p.is_ddo_by_me = p.ddomoongs.filter(from_user=request.user).exists()
            participation.other_participants = other_participants
        else:
            participation.other_participants = []
    
    context = {
        'page_obj': page_obj,
        'total_count': my_participations.count(),
    }
    
    return render(request, 'users/mypage_participated_list.html', context)


# 다른 사용자 프로필 조회
@login_required
def user_profile(request, user_id):
    """다른 사용자 프로필 조회"""
    # 조회하려는 사용자
    profile_user = get_object_or_404(User, id=user_id)
    
    # 본인 프로필이면 마이페이지로 리다이렉트
    if profile_user == request.user:
        return redirect('users:mypage')
    
    context = {
        'profile_user': profile_user,
    }
    
    return render(request, 'users/user_profile.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('moong:main')
    
    if request.method == "POST":
        my_form = LoginForm(data=request.POST)
        if my_form.is_valid():
            username = my_form.cleaned_data["username"]
            password = my_form.cleaned_data["password"]
            my_user = authenticate(username=username, password=password)

            if my_user:
                login(request, my_user)
                return redirect('moong:main')
            else:
                my_form.add_error(None, "이메일과 비밀번호를 확인하세요.")

        context = {'form': my_form}
        return render(request, "users/login.html", context)
    
    else:
        my_form = LoginForm()
        context = {'form': my_form}
        return render(request, "users/login.html", context)

    
def logout_view(request):
    logout(request)
    return redirect("users:login")