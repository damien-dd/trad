from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def strip_url_lang_prefix(url):
	if len(url) > 4 and url[0] == '/' and url[3] == '/':
		return url[3:]
	else:
		return url

