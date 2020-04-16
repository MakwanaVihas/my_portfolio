from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import SignUp
from .models import User
# Register your models here.


class BaseUserAdmin(UserAdmin):
    add_form = SignUp
    list_display = ('email','first_name','last_name',)
    list_filter = ('email', 'first_name','last_name',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('full_name','first_name','last_name',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','first_name','last_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
admin.site.register(User, BaseUserAdmin)
