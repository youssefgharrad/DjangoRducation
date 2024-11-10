# Generated by Django 5.1.1 on 2024-10-28 17:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionLangue', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InputTranslator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_text', models.TextField(blank=True, null=True)),
                ('input_voice', models.FileField(blank=True, null=True, upload_to='gestionLangue/input_voice/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_translations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OutputTranslator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output_text', models.TextField(blank=True, null=True)),
                ('output_voice', models.FileField(blank=True, null=True, upload_to='gestionLangue/output_voice/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('input_translator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='output_translations', to='gestionLangue.inputtranslator')),
            ],
        ),
        migrations.DeleteModel(
            name='SortieVoice',
        ),
        migrations.DeleteModel(
            name='Voice',
        ),
    ]