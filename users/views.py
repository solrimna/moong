from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm
from .models import User
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from locations.models import Location
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from moong.models import Post, Participation


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
            return redirect("/admin/")   # 임시 확인용
        else:
            print("❌ FORM ERRORS:", form.errors)

    else:
        form = SignupForm()
       
    context = {"form":form}

    return render(request, "users/signup.html", context)



# 마이페이지 조회
@login_required  # 로그인한 사용자만 접근 가능
def mypage(request):
    """마이페이지 - 프로필 조회"""
    user = request.user  # 현재 로그인한 사용자
    
    context = {
        'user': user,
    }
    
    return render(request, 'users/mypage.html', context)


# 프로필 수정
@login_required
def mypage_edit(request):
    """마이페이지 - 프로필 수정"""
    user = request.user
    locations = Location.objects.all()  # 모든 지역 목록
    
    if request.method == 'POST':
        # 프로필 이미지 수정
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
            messages.success(request, '프로필 이미지가 변경되었습니다.')
        
        # 자기소개 수정
        bio = request.POST.get('bio')
        if bio is not None:  # 빈 문자열도 허용
            user.bio = bio
            messages.success(request, '자기소개가 변경되었습니다.')
        
        # 지역 수정
        location_id = request.POST.get('location')
        if location_id:
            try:
                user.location = Location.objects.get(id=location_id)
                messages.success(request, '주 활동 지역이 변경되었습니다.')
            except Location.DoesNotExist:
                messages.error(request, '유효하지 않은 지역입니다.')
        
        # 성별 공개 여부 수정
        gender_visible = request.POST.get('gender_visible')
        user.gender_visible = (gender_visible == 'on')  # 체크박스는 'on' 또는 None
        
        user.save()
        return redirect('users:mypage')
    
    context = {
        'user': user,
        'locations': locations,
    }
    
    return render(request, 'users/mypage_edit.html', context)


# 활동 이력
@login_required
def mypage_activity(request):
    """마이페이지 - 활동 이력"""
    user = request.user
    
    # 내가 만든 모임 (임시저장 제외, 완성된 글만)
    my_posts = Post.objects.filter(
        author=user,
        complete=True  # 완성된 글만 (임시저장 제외)
    ).order_by('-create_time')
    
    # 내가 참여한 모임 (승인된 참여만, 완성된 글만)
    my_participations = Participation.objects.filter(
        user=user,
        status='APPROVED',
        post__complete=True  # 완성된 글만
    ).select_related('post').order_by('-create_time')
    
    # 통계
    total_created = my_posts.count()
    total_participated = my_participations.count()
    
    context = {
        'user': user,
        'my_posts': my_posts,
        'my_participations': my_participations,
        'total_created': total_created,
        'total_participated': total_participated,
    }
    
    return render(request, 'users/mypage_activity.html', context)


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