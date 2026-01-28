from django.db import models
from django.conf import settings


class Post(models.Model):
    """게시글 모델"""
    
    GENDER_CHOICES = [
        (0, '누구나'),
        (1, '남성만'),
        (2, '여성만'),
    ]
    
    # 게시글 기본 정보
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name='제목')
    content = models.TextField(null=False, blank=False, verbose_name='내용')
    
    # 모임 정보
    moim_date = models.DateField(null=False, blank=False, verbose_name='모임 날짜')
    moim_time = models.TimeField(null=False, blank=False, verbose_name='모임 시간')
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        verbose_name='모임 장소',
        db_column='location_id'
    )
    
    # 작성자
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='작성자',
        db_column='author_id'
    )
    
    # 인원 관리
    max_people = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name='최대 인원')
    
    # 상태 관리
    is_closed = models.BooleanField(null=True, blank=True, default=False, verbose_name='모임 마감 여부')
    is_cancelled = models.BooleanField(null=True, blank=True, default=False, verbose_name='폭파 여부')
    moim_finished = models.BooleanField(null=True, blank=True, default=False, verbose_name='모집 완료 여부')

    complete = models.BooleanField(null=True, blank=True, default=False, verbose_name='임시저장 여부')
    
    # 제한 정보
    gender_restriction = models.IntegerField(
        choices=GENDER_CHOICES,
        default=0,
        null=True,
        blank=True,
        verbose_name='성별 제한'
    )
    age_restriction = models.IntegerField(default=0, null=True, blank=True, verbose_name='나이 제한')
    
    # 타임스탬프
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    update_time = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    
    # 해시태그 연결 (ManyToMany)
    hashtags = models.ManyToManyField(
        'Hashtag',
        through='PostHashtag',
        related_name='posts',
        blank=True,
        verbose_name='해시태그'
    )
    
    class Meta:
        ordering = ['-create_time']
        verbose_name = '게시글'
        verbose_name_plural = '게시글'
        db_table = 'Post'
    
    def __str__(self):
        return self.title if self.title else f'게시글 {self.id}'
    
    def get_approved_count(self):
        """승인된 참여자 수"""
        return self.participations.filter(status='APPROVED').count()
    
    def get_pending_count(self):
        """승인 대기 중인 신청자 수"""
        return self.participations.filter(status='PENDING').count()
    
    def is_full(self):
        """정원 마감 여부"""
        if self.max_people is None:
            return False
        return self.get_approved_count() >= self.max_people
    
    def can_approve_more(self):
        """추가 승인 가능 여부"""
        if self.max_people is None:
            return True
        return self.get_approved_count() < self.max_people
    
    def is_published(self):
        """게시 여부 (임시저장 아님)"""
        return self.complete == True
    
    def get_gender_restriction_display_custom(self):
        """성별 제한 한글 표시"""
        gender_map = {0: '누구나', 1: '남성만', 2: '여성만'}
        return gender_map.get(self.gender_restriction, '누구나')
    
    def get_main_image(self):
        """대표 이미지 (첫 번째 이미지)"""
        return self.images.first()
    
    def get_image_count(self):
        """이미지 개수"""
        return self.images.count()
    
    def has_images(self):
        """이미지 존재 여부"""
        return self.images.exists()



class Participation(models.Model):
    """참여 상태 모델"""
    
    STATUS_CHOICES = [
        ('PENDING', '대기중'),
        ('APPROVED', '승인됨'),
        ('REJECTED', '거절됨'),
        ('CANCELLED', '취소'),
        ('COMPLETED', '완료'),
    ]
    
    # 연결 정보
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name='게시글',
        db_column='post_id'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name='회원',
        db_column='user_id'
    )
    
    # 상태
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='참여 상태'
    )
    
    # 타임스탬프
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='신청 시간')
    update_time = models.DateTimeField(auto_now=True, verbose_name='상태 변경 시간')
    approve_time = models.DateTimeField(null=True, blank=True, verbose_name='승인 시간')
    
    class Meta:
        unique_together = [['post', 'user']]
        ordering = ['create_time']
        verbose_name = '참여 상태'
        verbose_name_plural = '참여 상태'
        db_table = 'Participation'
    
    def __str__(self):
        return f'{self.user.username} - {self.post.title} ({self.get_status_display()})'
    
    def approve(self):
        """승인 처리"""
        from django.utils import timezone
        self.status = 'APPROVED'
        self.approve_time = timezone.now()
        self.save()
    
    def reject(self):
        """거절 처리"""
        self.status = 'REJECTED'
        self.save()
    
    def cancel(self):
        """취소 처리"""
        self.status = 'CANCELLED'
        self.save()


class Comment(models.Model):
    """댓글 모델"""
    
    # 연결 정보
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='게시글',
        db_column='post_id'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='작성자',
        db_column='author'
    )
    
    # 댓글 내용
    content = models.TextField(null=False, blank=False, verbose_name='댓글 내용')
    
    # 주최자 여부
    is_author = models.BooleanField(null=True, blank=True, verbose_name='주최자 댓글 여부')
    
    # 대댓글 구조
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='부모 댓글',
        db_column='parent_id'
    )
    
    # 타임스탬프
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    update_time = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    
    class Meta:
        ordering = ['create_time']
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
        db_table = 'Comment'
    
    def __str__(self):
        return f'{self.author.username}의 댓글 - {self.content[:20] if self.content else ""}'
    
    def save(self, *args, **kwargs):
        """저장 시 주최자 여부 자동 설정"""
        if self.author == self.post.author:
            self.is_author = True
        else:
            self.is_author = False
        super().save(*args, **kwargs)
    
    def get_replies(self):
        """대댓글 목록"""
        return self.replies.all()
    
    def is_reply(self):
        """대댓글 여부"""
        return self.parent is not None


class Hashtag(models.Model):
    """해시태그 모델"""
    
    name = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        verbose_name='해시태그명'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    
    class Meta:
        ordering = ['name']
        verbose_name = '해시태그'
        verbose_name_plural = '해시태그'
        db_table = 'Hashtag'
    
    def __str__(self):
        return f'#{self.name}' if self.name else f'해시태그 {self.id}'
    
    def save(self, *args, **kwargs):
        """저장 시 '#' 제거 및 공백 제거"""
        if self.name:
            self.name = self.name.lstrip('#').strip()
        super().save(*args, **kwargs)
    
    def get_post_count(self):
        """이 해시태그를 사용하는 게시글 수"""
        return self.posts.count()


class PostHashtag(models.Model):
    """게시글-해시태그 중간 테이블"""
    
    hashtag = models.ForeignKey(
        'Hashtag',
        on_delete=models.CASCADE,
        verbose_name='해시태그',
        db_column='hashtag_id'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='게시글',
        db_column='post_id'
    )
    
    class Meta:
        unique_together = [['post', 'hashtag']]
        verbose_name = '게시글-해시태그'
        verbose_name_plural = '게시글-해시태그'
        db_table = 'PostHashtag'
    
    def __str__(self):
        return f'{self.post.title} - #{self.hashtag.name}'
    

class Image(models.Model):  
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='게시글',
        db_column='post_id'
    )
    order = models.IntegerField(default=0, verbose_name='순서')
    image = models.ImageField(
        upload_to='post_images/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='이미지'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='업로드 시간')
    
    class Meta:
        ordering = ['order', 'create_time']
        verbose_name = '게시글 이미지'
        verbose_name_plural = '게시글 이미지'
        db_table = 'image'
    
    def __str__(self):
        return f'{self.post.title} - 이미지 {self.order}'    