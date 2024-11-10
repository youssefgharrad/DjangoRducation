from django.contrib import admin
from .models import Course
from .models import CoursParticiperParUser

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'specialites', 'niveau', 'user']
    list_filter = ['specialites', 'niveau']
    search_fields = ['title', 'specialites', 'niveau']
    list_per_page = 10
    list_editable = ['specialites', 'niveau']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image', 'pdf', 'user')
        }),
        ('Spécialités et Niveau', {
            'fields': ('specialites', 'niveau')
        }),
    )

    ordering = ['user']

    def save_model(self, request, obj, form, change):
        if not change or not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(CoursParticiperParUser)
class CoursParticiperParUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'date_participation']
    list_filter = ['date_participation']
    search_fields = ['user__username', 'course__title']

