from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User



@admin.register(User)
class CustomUserAdmin(UserAdmin):
	list_display = ('username', 'email', 'role', 'is_staff')
	list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')

	fieldsets = (
			(None, {'fields': ('role',),}),
		) + UserAdmin.fieldsets

	add_fieldsets = (
			(None, {'fields': ('role',),}),
		) + UserAdmin.add_fieldsets

