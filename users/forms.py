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

    gender = forms.ChoiceField(
        choices=[
        ("", "성별 선택"),
        ("M", "남성"),
        ("F", "여성")
        ],
        label="성별",      
        required=False,
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

 
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "password1",
            "password2",
            "nick_name",
            "location",
            "profile_image",
            "phone",
            "gender",
            "email",
            )
    
    
        
    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")

        return email


    def save(self, commit=True):
        user = super().save(commit=False)

        # ⭐ 핵심: username에 email 넣기
        user.username = self.cleaned_data["email"]

        if commit:
            user.save()
        return user    


class LoginForm(forms.Form):
    username = forms.EmailField(
        label = "이메일 주소",
        widget=forms.EmailInput(
            attrs={"placeholder": "example@email.com"},
        ),
    )
    password = forms.CharField(
        label = "비밀번호",
        widget=forms.PasswordInput(
            attrs={"placeholder": "비밀번호를 입력하세요."},
        ),
    )


# ===== 프로필 수정 전용 폼 (닉네임, 이메일, 전화번호 수정 불가) =====
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image', 'bio', 'gender_visible']  # location 제거 (HTML에서 직접 전송)
        widgets = {
            'profile_image': forms.FileInput(
                attrs={
                    'class': 'file-input',
                    'accept': 'image/jpeg,image/png'
                }
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'form-textarea',
                    'rows': 4,
                    'placeholder': '간단한 자기소개를 작성해주세요'
                }
            ),
            'gender_visible': forms.CheckboxInput(
                attrs={'class': 'checkbox-input'}
            ),
        }
        labels = {
            'profile_image': '프로필 사진',
            'bio': '자기소개',
            'gender_visible': '성별 공개',
        }
    
    # 프로필 이미지 검증
    profile_image = forms.ImageField(
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png']
            )
        ],
        error_messages={
            'invalid': '이미지 파일만 업로드할 수 있습니다.',
        },
    )