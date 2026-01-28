from django import forms
from .models import Post
from locations.models import Location

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
        location_id = self.data.get("location")
        if location_id:
            self.fields["location"].queryset = Location.objects.filter(
                id=location_id
            )
