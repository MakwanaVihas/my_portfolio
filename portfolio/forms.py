import django.forms as forms
from django.contrib.auth.forms import UserCreationForm
from . import models

class SignUp(UserCreationForm):

    class Meta:
        model = models.User
        fields = ("first_name","last_name","email","password1","password2")

class Login(forms.Form):
    email = forms.EmailField(required = True)
    password = forms.CharField(required = True,widget = forms.PasswordInput())

class TickerForm(forms.ModelForm):
    
    class Meta:
        model = models.Ticker
        fields = "__all__"
