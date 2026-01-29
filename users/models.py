# users/models.py

from django.contrib.auth.models import AbstractUser
from locations.models import Location
from django.core.validators import RegexValidator
from django.db import models

phone_regex = RegexValidator(
    regex = r"^010-\d{4}-\d{4}$",
    message="전화번호는 010-XXXX-XXXX 형식이어야 합니다."
    )

class User(AbstractUser):

    
    # 기본 프로필 정보
    nick_name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='닉네임'
    )

    profile_image = models.ImageField(
        upload_to='profile_images/%Y/%m/%d/',
        blank=True, 
        null=True,  
        verbose_name='프로필 이미지'
    )
    # 추가할 필드
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='자기소개'
    )

    location = models.ForeignKey('locations.Location',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='user_location',
                                help_text="기본 활동 지역",
                                db_column='location_id',
                                verbose_name='주소'
    )
    
    # 활동 정보
    ddomoong = models.IntegerField(
        default=0, 
        verbose_name='또뭉(좋아요 수)'
    )
        
    # 개인 정보
    phone = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name='전화번호',
        validators=[phone_regex]
    )

    gender = models.CharField(
        max_length=1,
        choices=[('M', '남성'), ('F', '여성'), ('O', '기타')],
        null=True,
        blank=True,
        verbose_name='성별'
    )
    gender_visible = models.BooleanField(
        default=True,
        verbose_name='성별 공개'
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        db_table = 'users'  # 테이블명을 'users'로 지정
        ordering = ['-date_joined']  # 역순 정렬 추가  

    def __str__(self):
        return self.nick_name 
    
    def increase_ddomoong(self):
        """또뭉 증가"""
        self.ddomoong += 1
        self.save(update_fields=['ddomoong']) 
    
    def decrease_ddomoong(self):
        """또뭉 감소"""
        if self.ddomoong > 0:
            self.ddomoong -= 1
            self.save(update_fields=['ddomoong'])



    email = models.EmailField(unique = True,
                              blank=False,
                              help_text="이메일 주소")

    


    

