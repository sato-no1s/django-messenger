from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model


class UserUpdateForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['last_name','first_name']
        labels = {
            'last_name' : '姓',
            'first_name' : '名',
        }