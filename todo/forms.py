from django import forms
from .models import ToDo

class TodoForm(forms.ModelForm):
    class Meta:
        model = ToDo
        fields = ['title', 'description', 'due_date', 'status']  # Inclure 'status' ici
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre de la tâche'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez la tâche',
                'rows': 4
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sélectionnez une date',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, is_update=False, **kwargs):
        super(TodoForm, self).__init__(*args, **kwargs)
        
        # Si c'est une mise à jour, garder le champ 'status'
        if is_update:
            self.fields['status'].widget.attrs.update({
                'class': 'form-control',  # Optionnel: vous pouvez ajouter d'autres attributs si nécessaire
            })
        else:
            # Si c'est une création, retirer 'status' des champs
            self.fields.pop('status')

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',  # Ajoutez cette classe pour tous les champs
                'placeholder': field.label  # Utilisez le label comme texte de remplissage
            })
