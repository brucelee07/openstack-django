from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Vm

# 用户注册表单
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]


class VmForm(forms.ModelForm):
    class Meta:
        model = Vm
        fields = ["vmname"]
