from django.shortcuts import render, redirect
from django.utils import translation
from .forms import RegisterForm
from django.conf import settings


def home(request):
	return render(request, 'base.html')

def register(response):
	print (settings.LOCALE_PATHS)
	if response.method == "POST":
		form = RegisterForm(response.POST)
		if form.is_valid():
			form.save()

		return redirect("/")
	else:
		form = RegisterForm(initial={'role': None})

	return render(response, "registration/register.html", {"form":form})
