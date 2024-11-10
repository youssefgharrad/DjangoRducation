from django.contrib import admin
from .models import InputTranslator, OutputTranslator

# Register and customize InputTranslator in the admin panel
@admin.register(InputTranslator)
class InputTranslatorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "input_text", "input_voice", "created_at")  # Fields to display in the list view
    search_fields = ("user__username", "input_text")  # Enable searching by user or text content
    list_filter = ("created_at", "user")  # Filter by creation date or user
    ordering = ("-created_at",)  # Order by most recent entries

# Register and customize OutputTranslator in the admin panel
@admin.register(OutputTranslator)
class OutputTranslatorAdmin(admin.ModelAdmin):
    list_display = ("id", "input_translator", "output_text", "output_voice", "created_at")  # Display fields
    search_fields = ("input_translator__user__username", "output_text")  # Enable search by input's user or text content
    list_filter = ("created_at", "input_translator")  # Filter by creation date or input reference
    ordering = ("-created_at",)  # Order by most recent entries
