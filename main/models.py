# -*- coding: utf-8 -*-
import requests

from django.db import models
from django.db.models import Count, F
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.conf import settings



@deconstructible
class CustomUsernameValidator(validators.RegexValidator):
	regex = r'^[\w.+-]+\Z'
	message = 'Saisissez un nom d\'utilisateur valide. Il ne peut contenir que des lettres, des nombres ou les caractères, « . », « + », « - » et « _ ».'
	flags = 0


class User(AbstractUser):
	ROLE_OPTIONS = [
		('CO', _('Contributor')),
		('TR', _('Translator')),
		('VI', _('Videographer')),
	]
	username = models.CharField(_('username'), max_length=150, unique=True,
		help_text='Requis. 150 caractères maximum. Uniquement des lettres, nombres et les caractères, « . », « + », « - » et « _ ».',
		validators=[CustomUsernameValidator()],
		error_messages={
			'unique': _("A user with that username already exists."),
		},
	)
	
	email = models.EmailField(_('email address'), unique=True)
	is_email_verified = models.BooleanField('email vérifié', default=False)
	verification_code = models.CharField(_('verification code'), max_length=10, default='', blank=True)

	role = models.CharField(_('role'), max_length=2, choices=ROLE_OPTIONS, blank=False, default=ROLE_OPTIONS[0][0])
	
	@property
	def is_translator(self):
		return self.role in ['TR', 'VI']


def channel_directory_path(instance, filename): 
	# file will be uploaded to MEDIA_ROOT / channel_<id>/<filename> 
	return 'channel_{0}/{1}'.format(instance.id, filename)


class Channel(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	url = models.CharField(_('url'), max_length=100)
	title = models.CharField(_('title'), max_length=100, default='')
	descr = models.TextField(_('description'), blank=True, default='')
	image = models.ImageField(upload_to = channel_directory_path, blank=True, null=True)
	is_verified = models.BooleanField('verified', default=False)

	@classmethod
	def create(cls, url):
		src = cls(url=url)
		return src

	@property
	def image_url(self):
		"""
		Return self.image.url if self.image is not None, 
		'url' exist and has a value, else, return None.
		"""
		if self.image:
			return getattr(self.image, 'url', None)
		else:
			return None


class Source(models.Model):
	PLATFORM_CHOICES = [
		('YT', _('Youtube')),
		('PT', _('Peertube')),
	]

	url = models.CharField(_('url'), max_length=100)
	platform_url = models.CharField(_('platform url'), max_length=50, blank=True, default='')
	platform_type = models.CharField(_('platform type'), max_length=2, choices=PLATFORM_CHOICES, blank=True, default='')
	video_id = models.CharField(_('video id'), max_length=50, blank=True, default='')

	@classmethod
	def create(cls, url):
		platform_type = ''
		video_id = ''
		if '://www.youtube.com' in url or '://youtu.be' in url:
			platform_type = 'YT'
			if '?v=' in url:
				video_id = url.split('?v=', 1)[1][:11]
			elif '%3Fv%3D' in url:
				video_id = url.split('%3Fv%3D', 1)[1][:11]
			elif '/youtu.be/' in url:
				video_id = url.split('/youtu.be/', 1)[1][:11]
		src = cls(url=url, platform_type=platform_type, video_id=video_id)
		return src

	def get_embed_url(self):
		if self.platform_type == 'YT':
			return 'https://www.youtube.com/embed/'+self.video_id
		return ''

	def fetch_title(self):
		try:
			resp = requests.get('https://noembed.com/embed', params={'url': self.url})
			if resp.status_code == 200:
				return resp.json().get('title', '')
		except requests.exceptions.RequestException as e:
			pass
		return ''

	def __str__(self):
		return self.url


class Video(models.Model):
	LANGUAGE_CHOICES = [
		('en', _('English')),
		#('fr', _('French')),
		('de', _('German')),
		('es', _('Spanish')),
		('it', _('Italian')),
	]

	source = models.ForeignKey(Source, on_delete=models.PROTECT)
	title = models.CharField(_('title'), max_length=100, blank=True, default='')
	descr = models.TextField(_('description'), blank=True, default='')
	lang = models.CharField(_('language'), max_length=2, choices=LANGUAGE_CHOICES)
	tags = models.CharField(max_length=255, blank=True, default='',
		help_text='Utilisez une virgule « , » pour saisir plusieurs tags.')
	submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	submitted_at = models.DateTimeField(auto_now_add=True)
	done = models.BooleanField(_('done'), default=False)
	votes = models.IntegerField(blank=True, default=0)

	def __str__(self):
		return self.title

	def tags_list(self):
		return self.tags.split(',')

	def comments(self):
		return self.videocomment_set.order_by('posted_at')

	def translation_files(self):
		return self.videofile_set.filter(lang__in=['fr', F('lang')])

	def transcripts_original(self):
		return self.videofile_set.filter(lang=self.lang, group='TR')

	def subtitles_original(self):
		return self.videofile_set.filter(lang=self.lang, group='SUB')

	def transcripts_translated(self):
		return self.videofile_set.filter(lang='fr', group='TR')

	def subtitles_translated(self):
		return self.videofile_set.filter(lang='fr', group='SUB')

	def translation_status(self):
		translations = []
		done = self.translation_files().values('lang', 'group').annotate(total=Count('lang')).values_list('group', 'lang')
		for translation in [('TR', self.lang), ('TR', 'fr'), ('SUB', self.lang), ('SUB', 'fr')]:
			translations.append(translation + (translation in done, ))
		return translations


class VideoVote(models.Model):
	video = models.ForeignKey(Video, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	value = models.SmallIntegerField(default=1)
	
	class Meta:
		unique_together = ('video', 'user', )


class VideoComment(models.Model):
	video = models.ForeignKey(Video, on_delete=models.CASCADE)
	author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	comment = models.TextField(_('comment'))
	posted_at = models.DateTimeField(auto_now_add=True)


def file_upload(instance, filename):
	"""Stores the attachment in a "per video/primary key" folder"""
	return "video/{video}/{filename}".format(
		video=instance.video.pk,
		filename=filename,
	)

class VideoFile(models.Model):
	LANGUAGE_CHOICES = [
		('en', _('English')),
		('fr', _('French')),
		('de', _('German')),
		('es', _('Spanish')),
		('it', _('Italian')),
	]

	GROUPS = [
		('TR', _('Transcript')),
		('SUB', _('Subtitle')),
	]

	video = models.ForeignKey(Video, on_delete=models.CASCADE)
	group = models.CharField(max_length=3, choices=GROUPS, blank=True, default='', verbose_name=_('group'))
	lang = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_('language'))
	creator = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name=_("creator"),
		on_delete=models.CASCADE,
	)
	upload = models.FileField(
		_("file"), upload_to=file_upload
	)
	created = models.DateTimeField(_("created"), auto_now_add=True)
	modified = models.DateTimeField(_("modified"), auto_now=True)

