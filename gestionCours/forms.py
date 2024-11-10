from django import forms
from .models import Course, Chapitre

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'specialites', 'niveau', 'image', 'pdf']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre du cours'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez le cours',
                'rows': 4
            }),
            'specialites': forms.Select(attrs={
                'class': 'form-control'
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
            'pdf': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': field.widget.attrs.get('class', '') + ' form-control',
                'placeholder': field.label
            })


class ChapitreForm(forms.ModelForm):
    class Meta:
        model = Chapitre
        fields = ['title', 'description', 'categorie', 'document']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre du chapitre'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez le chapitre',
                'rows': 4
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ChapitreForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': field.widget.attrs.get('class', '') + ' form-control',
                'placeholder': field.label
            })
