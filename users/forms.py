from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from locations.models import Location
from django.core.validators import FileExtensionValidator

class SignupForm(UserCreationForm): # UsercreationForm은 ModelForm

    nick_name = forms.CharField(
        max_length=100,
        label="닉네임",
        widget=forms.TextInput(attrs={"placeholder": "사용할 닉네임을 입력하세요"})
        
    )
    # ModelForm에서는 직접 선언한 필드가 자동 생성 필드보다 우선이다

    profile_image = forms.ImageField(
        label = "프로필 이미지",
        required = False,
        help_text = "JPG, PNG 파일만 가능",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
            ],
        widget=forms.ClearableFileInput(
            attrs={
                # "class": "form-control",
                "accept": "image/jpeg,image/png",
            }
        ),  
        error_messages={
            "invalid": "이미지 파일만 업로드할 수 있습니다.",
            # "required": "프로필 이미지를 업로드해주세요.",
        },  

    )


    location = forms.ModelChoiceField(
        queryset=Location.objects.none(), 
        # forms.py 실행시에는 빈queryset호출
        # queryset : DB와 연결 되어 DB에 실제로 존재하는 선택지만 허용
        # ModelChoiceField + queryset를 사용(ChoiceField와의 차이점)
        label="활동 지역 선택",
        widget=forms.Select(attrs={"class" : "form-select"}), 
        required=True,
    )
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs) #부모(UserCreationForm)가 하던 기본 세팅 전부 실행
        location_id = self.data.get("location")
        if location_id:
            self.fields["location"].queryset = Location.objects.filter(
                id=location_id
            )

    phone = forms.CharField(
        required = True,
        widget=forms.TextInput(
            attrs = {"placeholder" : "010-XXXX-XXXX"}
        )
    )        

    email = forms.EmailField(
        required = True, 
        widget= forms.EmailInput(
            attrs = {"placeholder": "example@email.com"}
        )
    )

 
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "nick_name",
            "location",
            "profile_image",
            "email",
            "phone",
            )
    
    
    email = forms.EmailField(required=True)    
    
    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")

        return email    