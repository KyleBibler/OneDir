__author__ = 'Owner'

from django import forms
# from models import UserProfile
from oneDirApp.models import UserProfile
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username','password',)