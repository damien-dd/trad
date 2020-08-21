from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import ReCaptchaField

from django_select2.forms import Select2TagWidget

from .models import User, Video, Channel, VideoFile, VideoComment


class RegisterForm(UserCreationForm):
	email = forms.EmailField()
	channel = forms.CharField(max_length=100, required=False)
	captcha = ReCaptchaField()

	class Meta:
		model = User
		fields = ['role', 'username', 'email', 'password1', 'password2']
		widgets = {
            'role': forms.RadioSelect,
        }
		labels = {
			'role': _('You are'),
		}


class TagsWidget(Select2TagWidget):

	def value_from_datadict(self, data, files, name):
		values = super().value_from_datadict(data, files, name)
		return ",".join(values)

	def optgroups(self, name, value, attrs=None):
		values = value[0].split(',') if value[0] else []
		selected = set(values)
		subgroup = [self.create_option(name, v, v, selected, i) for i, v in enumerate(values)]
		return [(None, subgroup, 0)]


class AddVideoForm(forms.ModelForm):
	url = forms.CharField(max_length=100)

	class Meta:
		model = Video
		fields = ('url', 'lang', 'tags', )
		widgets = {
			'tags': TagsWidget(attrs={'data-token-separators': ','}),
		}


class MyChannelForm(forms.ModelForm):
	class Meta:
		model = Channel
		exclude = ('user', 'url', 'is_verified', )


class VideoFileForm(forms.ModelForm):
	class Meta:
		model = VideoFile
		fields = ['upload', ]


class VideoCommentForm(forms.ModelForm):
	class Meta:
		model = VideoComment
		fields = ['comment', ]
		widgets = {
			'comment': forms.Textarea(attrs={'rows':4, 'cols':40}),
		}
		

class SearchForm(forms.Form):
	done = forms.BooleanField(required=False, initial=False)
	text = forms.CharField(max_length=50)


