from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Detail, Request, Alumni

class RequestAdmin(admin.ModelAdmin):
    search_fields = ('ticket_crsid', 'ticket_last_name', 'ticket_first_name')

admin.site.register(Request, RequestAdmin)
admin.site.register(Alumni)

class RequestInline(admin.StackedInline):
    model = Request
    extra = 0

class DetailInline(admin.StackedInline):
    model = Detail

class CustomUserAdmin(UserAdmin):
	fieldsets = [
        (None,               {'fields': ['username', 'password']}),
        ('Personal Information', {'fields': ['first_name', 'last_name', 'email']}),
    ]

	inlines = [DetailInline, RequestInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)