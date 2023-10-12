from django import forms
from django.contrib.auth.models import User
from account.models import Comment


class AdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PageNumberForm(forms.Form):
    page = forms.IntegerField(label='Page Number', min_value=1)

class TenantEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        
class SearchForm(forms.Form):
    query = forms.CharField()