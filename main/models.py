# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = [
		('EN', _('English')),
		('FR', _('French')),
		('ES', _('Spanish')),
		('SE', _('Swedish')),
	]

class User(AbstractUser):
	ROLE_OPTIONS = [
		('CO', _('Contributor')),
		('TR', _('Translator')),
		('VI', _('Videographer')),
	]

	role = models.CharField(_('role'), max_length=2, choices=ROLE_OPTIONS, blank=False, default=ROLE_OPTIONS[0][0])
	channel = models.CharField(_('channel'), max_length=100, blank=True, default='')

