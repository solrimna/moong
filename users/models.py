# users/models.py

from django.contrib.auth.models import AbstractUser
from locations.models import Location
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

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
        default='profile_images/custom_property.png',
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

    email = models.EmailField(
        unique=True,
        blank=False,
        help_text="이메일 주소"
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        db_table = 'users'
        ordering = ['-date_joined']

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
            
    def save(self, *args, **kwargs):
        # 🔥 새로 업로드된 이미지만 처리 (기본 이미지나 이미 저장된 이미지는 건너뛰기)
        if self.profile_image and hasattr(self.profile_image, 'file'):
            try:
                img = Image.open(self.profile_image)

                if img.mode != "RGB":
                    img = img.convert("RGB")

                width, height = img.size
                min_side = min(width, height)

                left = (width - min_side) // 2
                top = (height - min_side) // 2
                right = left + min_side
                bottom = top + min_side

                img = img.crop((left, top, right, bottom))
                img = img.resize((300, 300), Image.LANCZOS)

                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                buffer.seek(0)

                # 파일명 유지
                self.profile_image = ContentFile(
                    buffer.read(),
                    name=self.profile_image.name
                )
            except Exception:
                # 이미지 처리 실패 시 원본 유지
                pass

    
        super().save(*args, **kwargs)
    


    

