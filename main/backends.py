from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailOrUsernameModelBackend(ModelBackend):
	def authenticate(self, request, username=None, password=None):
		print ('username: %s' % username)
		if '@' in username:
			kwargs = {'email': username}
		else:
			kwargs = {'username': username}
		try:
			user = User.objects.get(**kwargs)
			if user.check_password(password) and (user.is_email_verified or user.is_superuser):
				return user
		except User.DoesNotExist:
			return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
