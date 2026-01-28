from django import forms
from .models import Post
from locations.models import Location
from django.utils import timezone

class PostForm(forms.ModelForm):

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(), 
        # forms.py 실행시에는 빈queryset호출
        # queryset : DB와 연결 되어 DB에 실제로 존재하는 선택지만 허용
        # ModelChoiceField + queryset를 사용(ChoiceField와의 차이점)
        label="모임 지역 선택",
        widget=forms.Select(attrs={"class" : "form-select"}), 
        required=False,
    )
    class Meta:
        model = Post
        fields = [
            'title', 
            'content',
            'moim_date', 
            'moim_time',
            'max_people',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '내용을 입력하세요'
            }) ,
            'moim_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type' : 'date'
            }) , 
            'moim_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type' : 'time'
            }),
            'max_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '최대 인원(선택)',
                'min' : 2
            }),
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'moim_date': '날짜',
            'moim_time': '시간',
            'max_people': '최대 인원',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 초기 생성 확인 용
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None 

        location_id = self.data.get("location")
        if location_id:
            self.fields["location"].queryset = Location.objects.filter(
                id=location_id
            )

    def clean(self):
        cleaned_data = super().clean()
        moim_date = cleaned_data.get('moim_date')
        moim_time = cleaned_data.get('moim_time')

        # 새 게시글 작성 시에만 검증 
        if not self.instance_pk:
            if moim_date and moim_time:
                # 현재 시간 (한국 시간 기준)
                now = timezone.now()
                today = now.date()
                current_time = now.time()
                
                # 모임 날짜가 과거인 경우
                if moim_date < today:
                    raise forms.ValidationError('모임 날짜는 과거가 될 수 없습니다.')
                
                # 모임 날짜가 오늘인데 시간이 현재보다 이른 경우
                if moim_date == today and moim_time < current_time:
                    raise forms.ValidationError(f'모임 시간은 현재 시간({current_time.strftime("%H:%M")}) 이후여야 합니다.')        
        return cleaned_data