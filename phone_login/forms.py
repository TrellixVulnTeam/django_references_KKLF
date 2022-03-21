from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User


class UserCreationForm(BaseUserCreationForm):
    phone_number = forms.CharField(max_length=20, required=True, help_text='Phone number')
    invite_code = forms.CharField(max_length=6, required=False, help_text='Invite code')
    # private_code = forms.CharField(max_length=6, required=False, help_text='Private code')


    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password1', 'password2')


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, help_text='Enter code')