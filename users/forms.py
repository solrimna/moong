# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from locations.models import Location
from django.core.validators import FileExtensionValidator

class SignupForm(UserCreationForm):
    nick_name = forms.CharField(
        max_length=100,
        label="닉네임",
        widget=forms.TextInput(attrs={"placeholder": "사용할 닉네임을 입력하세요"})
    )

    profile_image = forms.ImageField(
        label="프로필 이미지",
        required=False,
        help_text="JPG, PNG 파일만 가능",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ],
        widget=forms.ClearableFileInput(
            attrs={
                "accept": "image/jpeg,image/png",
            }
        ),
        error_messages={
            "invalid": "이미지 파일만 업로드할 수 있습니다.",
        },
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        label="활동 지역 선택",
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        location_id = self.data.get("location")
        if location_id:
            self.fields["location"].queryset = Location.objects.filter(
                id=location_id
            )

    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "010-XXXX-XXXX"}
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "example@email.com"}
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
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.EmailField(
        label="이메일 주소",
        widget=forms.EmailInput(
            attrs={"placeholder": "example@email.com"},
        ),
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={"placeholder": "비밀번호를 입력하세요."},
        ),
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image', 'bio', 'gender_visible']
        widgets = {
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
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'file-input',
                'accept': 'image/jpeg,image/png'
            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png']
            )
        ],
        error_messages={
            'invalid': '이미지 파일만 업로드할 수 있습니다.',
        },
    )