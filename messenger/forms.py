from django import forms

from .models import Group
from .models import Message


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={
                'autofocus' : True,
            }),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body' : forms.Textarea(attrs={
                'autofocus' : True,
                'rows' : 3,
            }),
        }