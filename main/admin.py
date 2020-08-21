from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Video, Source, Channel, VideoFile, VideoComment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	list_display = ('username', 'email', 'is_email_verified', 'role', 'is_staff')
	list_filter = ('role', 'is_email_verified', 'is_staff', 'is_superuser', 'is_active', 'groups')

	fieldsets = (
			(None, {'fields': ('role', 'is_email_verified', 'verification_code',),}),
		) + UserAdmin.fieldsets

	add_fieldsets = (
			(None, {'fields': ('role',),}),
		) + UserAdmin.add_fieldsets


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
	list_display = ('url', 'platform_type', )
	readonly_fields = ('url', )


class VideoCommentInline(admin.TabularInline):
	model = VideoComment
	extra = 1

class VideoFileInline(admin.TabularInline):
	model = VideoFile
	extra = 1


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
	list_display = ('title', 'lang', 'submitted_by', 'submitted_at', 'votes', 'done')
	list_filter = ('lang', 'submitted_by', 'submitted_at', 'done', )
	ordering = ('-submitted_at', )

	readonly_fields = ('source', )

	inlines = (VideoFileInline, VideoCommentInline, )

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
	list_display = ('url', 'title', 'user', 'is_verified', )

