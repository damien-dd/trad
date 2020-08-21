# -*- coding: utf-8 -*-
import string
import random
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils import translation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.template.loader import render_to_string
from django.http import JsonResponse

from .forms import RegisterForm, AddVideoForm, MyChannelForm, VideoFileForm, VideoCommentForm, SearchForm
from .models import Source, Video, Channel, User, VideoFile, VideoComment, VideoVote


def home(request):
	title2 = None
	videos = Video.objects.all()
	if request.method == 'POST':
		form_search = SearchForm(request.POST)
		if form_search.is_valid():
			done = form_search.cleaned_data.get('done')
			text = form_search.cleaned_data.get('text')
			videos = videos.filter(done=done, tags__icontains=text)
			title2 = 'Recherche \"%s\" dans les vidéos ' % text
			if done:
				title2 += 'faites (déjà traduites)'
			else:
				title2 += 'à faire (pas encore traduites)'
	else:
		form_search = SearchForm(initial={'done': True})

	if request.user.is_authenticated:
		user_votes = VideoVote.objects.filter(user=request.user).values_list('video_id', flat=True)
	else:
		user_votes = []
	
	return render(request, 'home.html', {
		'videos': videos.order_by('-votes', '-submitted_at'),
		'user_votes': user_votes,
		'form_search': form_search,
		'title2': title2})


def done(request):
	videos = Video.objects.filter(done=True).order_by('-votes', '-submitted_at')
	if request.user.is_authenticated:
		user_votes = VideoVote.objects.filter(user=request.user).values_list('video_id', flat=True)
	else:
		user_votes = []
	return render(request, 'home.html', {
		'videos': videos,
		'user_votes': user_votes,
		'title2': 'Videos faites (déjà traduites)'})


def todo(request):
	videos = Video.objects.filter(done=False).order_by('-votes', '-submitted_at')
	if request.user.is_authenticated:
		user_votes = VideoVote.objects.filter(user=request.user).values_list('video_id', flat=True)
	else:
		user_votes = []
	return render(request, 'home.html', {
		'videos': videos,
		'user_votes': user_votes,
		'search_todo': True,
		'title2': 'Videos à faire (pas encore traduites)'})


def tools(request):
	return render(request, 'tools.html')


def video(request, vidId):
	video = Video.objects.get(id=vidId)
	if not request.user.is_authenticated:
		return render(request, 'video.html', {'video': video})
	if request.method == "POST" and request.user.is_authenticated and (request.user.is_translator or request.user.is_staff):
		content_added = False
		form_tr_vo = VideoFileForm(request.POST, request.FILES, prefix='tr_vo')
		if form_tr_vo.is_valid() and form_tr_vo.cleaned_data.get('upload'):
			video_file = form_tr_vo.save(commit=False)
			video_file.video = video
			video_file.group = 'TR'
			video_file.lang = video.lang
			video_file.creator = request.user
			video_file.save()
			content_added = True

		form_tr_vf = VideoFileForm(request.POST, request.FILES, prefix='tr_vf')
		if form_tr_vf.is_valid() and form_tr_vf.cleaned_data.get('upload'):
			video_file = form_tr_vf.save(commit=False)
			video_file.video = video
			video_file.group = 'TR'
			video_file.lang = 'fr'
			video_file.creator = request.user
			video_file.save()
			content_added = True

		form_sub_vo = VideoFileForm(request.POST, request.FILES, prefix='sub_vo')
		if form_sub_vo.is_valid() and form_sub_vo.cleaned_data.get('upload'):
			video_file = form_sub_vo.save(commit=False)
			video_file.video = video
			video_file.group = 'SUB'
			video_file.lang = video.lang
			video_file.creator = request.user
			video_file.save()
			content_added = True

		form_sub_vf = VideoFileForm(request.POST, request.FILES, prefix='sub_vf')
		if form_sub_vf.is_valid() and form_sub_vf.cleaned_data.get('upload'):
			video_file = form_sub_vf.save(commit=False)
			video_file.video = video
			video_file.group = 'SUB'
			video_file.lang = 'fr'
			video_file.creator = request.user
			video_file.save()
			content_added = True
			video.done = True # french subtitle uploaded, mark the video has done
			video.save()

		form_comment = VideoCommentForm(request.POST, prefix='comment')
		if form_comment.is_valid():
			comment = form_comment.save(commit=False)
			comment.video = video
			comment.author = request.user
			comment.save()
			content_added = True

		if content_added:
			return redirect('video', vidId=vidId)

	else:
		form_tr_vo = VideoFileForm(prefix='tr_vo')
		form_tr_vf = VideoFileForm(prefix='tr_vf')
		form_sub_vo = VideoFileForm(prefix='sub_vo')
		form_sub_vf = VideoFileForm(prefix='sub_vf')
		form_comment = VideoCommentForm(prefix='comment')

	return render(request, 'video.html', {
		'video': video,
		'user_vote': VideoVote.objects.filter(user=request.user).first(),
		'form_tr_vo': form_tr_vo,
		'form_tr_vf': form_tr_vf,
		'form_sub_vo': form_sub_vo,
		'form_sub_vf': form_sub_vf,
		'form_comment': form_comment
	})


def channels(request):
	translators = User.objects.filter(role__in=['TR', 'VI']).order_by('username').values_list('username', flat=True)
	return render(request, 'channels.html', {
		'channels': Channel.objects.filter(is_verified=True),
		'translators': translators})


def theme(request, filename):
	request.session['bootstrap_theme'] = filename
	return redirect("/tools/")


@login_required
def edit_channel(request):
	instance = Channel.objects.filter(user=request.user).first()
	
	if request.method == "POST":
		form = MyChannelForm(request.POST, request.FILES, instance=instance)
		if form.is_valid():
			form.save()

		return redirect('edit_channel')
	else:
		form = MyChannelForm(instance=instance)

	return render(request, "channel.html", {'form':form, 'channel': instance})



@login_required
@transaction.atomic
def add_video(request):
	if request.method == "POST":
		form = AddVideoForm(request.POST)
		if form.is_valid():
			source = Source.create(form.cleaned_data.get('url'))
			source.save()

			video = form.save(commit=False)
			video.submitted_by = request.user
			video.source = source
			video.title = source.fetch_title()
			video.save()

		return redirect('home')
	else:
		form = AddVideoForm()

	return render(request, "add_video.html", {"form":form})



@login_required
def video_subtitle_delete(request, vidId, fileId):
	subtitle = VideoFile.objects.filter(id=fileId, video_id=vidId, group='SUB', creator=request.user).first()
	if subtitle:
		subtitle.delete()
	return redirect('video', vidId=vidId)


@login_required
def video_transcript_delete(request, vidId, fileId):
	transcript = VideoFile.objects.filter(id=fileId, video_id=vidId, group='TR', creator=request.user).first()
	if transcript:
		transcript.delete()
	return redirect('video', vidId=vidId)


@login_required
def video_comment_delete(request, vidId, commentId):
	comment = VideoComment.objects.filter(id=commentId, video_id=vidId, author=request.user).first()
	if comment:
		comment.delete()
	return redirect('video', vidId=vidId)


@transaction.atomic
def register(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		user = None
		if request.method == "POST":
			form = RegisterForm(request.POST)
			if form.is_valid():
				user = form.save(commit=False)

				# Generate a random verification code
				user.verification_code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for c in range(10))
				user.save()

				if form.cleaned_data.get('role') == 'VI':
					channel = Channel.create(form.cleaned_data.get('channel'))
					channel.user = user
					channel.save()

				# Email the verification link to the new user
				user.email_user('Vérification de votre adresse email',
					render_to_string('registration/verification_email.html', {
						'user': user, 'site_name': request.get_host(),
						'verify_url': request.build_absolute_uri(reverse('email_confirm', kwargs={'userId': user.id, 'token': user.verification_code})),
					}))
		else:
			form = RegisterForm(initial={'role': None})

		return render(request, "registration/register.html", {'form':form, 'user': user})


def email_confirm(request, userId, token):
	user = User.objects.filter(id=userId).first()
	if user and len(token) > 0 and user.verification_code == token:
		user.is_email_verified = True
		user.verification_code = ''
		user.save()

	verified = user and user.is_email_verified
	return render(request, "registration/verification_complete.html", {'verified': verified})


@login_required
def video_vote_add(request, vidId):
	obj, created = VideoVote.objects.get_or_create(video_id=vidId, user=request.user)
	total = VideoVote.objects.filter(video_id=vidId).count()
	Video.objects.filter(id=vidId).update(votes=total)
	return JsonResponse({'total': total, 'changed': created})


@login_required
def video_vote_remove(request, vidId):
	removed = VideoVote.objects.filter(video_id=vidId, user=request.user).delete()[0]
	total = VideoVote.objects.filter(video_id=vidId).count()
	Video.objects.filter(id=vidId).update(votes=total)
	return JsonResponse({'total': total, 'changed': removed})

