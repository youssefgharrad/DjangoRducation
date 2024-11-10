from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import UserLoginAttempt


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'diplomes', 'experience', 'specialite', 'about', 'avatar')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(UserLoginAttempt)
class UserLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp', 'ip_address', 'successful']
    list_filter = ['successful']
    search_fields = ['user__username', 'ip_address']
    ordering = ['-timestamp']
