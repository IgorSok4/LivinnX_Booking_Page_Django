from django import forms


class AdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PageNumberForm(forms.Form):
    page = forms.IntegerField(label='Page Number', min_value=1)
