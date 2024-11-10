from django.db import models
from django.conf import settings

class InputTranslator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    input_text = models.TextField(blank=True, null=True)
    input_voice = models.FileField(upload_to='gestionLangue/input_voice/', blank=True, null=True)

    def __str__(self):
        return f"InputTranslator {self.id} by User {self.user.id}"


class OutputTranslator(models.Model):
    input_translator = models.ForeignKey(InputTranslator, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    output_text = models.TextField(blank=True, null=True)
    output_voice = models.FileField(upload_to='gestionLangue/output_voice/', blank=True, null=True)

    def __str__(self):
        return f"OutputTranslator {self.id} for Input {self.input_translator.id}"


