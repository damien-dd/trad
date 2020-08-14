from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['role', 'username', 'email', 'password1', 'password2', 'channel']
		widgets = {
            'role': forms.RadioSelect,
        }
		labels = {
			'role': _('You are'),
		}

